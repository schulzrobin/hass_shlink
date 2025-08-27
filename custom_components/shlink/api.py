from __future__ import annotations

import asyncio
from typing import Any, Dict, Optional, Tuple
from urllib.parse import urlencode

import aiohttp

class ShlinkApiError(RuntimeError):
    pass

class ShlinkClient:
    def __init__(self, base_url: str, api_key: str, api_version: str = "3", session: Optional[aiohttp.ClientSession] = None):
        self._base = base_url.rstrip("/")
        self._key = api_key
        self._v = api_version
        self._session = session or aiohttp.ClientSession()

    async def close(self):
        if not self._session.closed:
            await self._session.close()

    def _headers(self) -> Dict[str, str]:
        return {"X-Api-Key": self._key, "Accept": "application/json"}

    def _url(self, path: str) -> str:
        return f"{self._base}/rest/v{self._v}{path}"

    async def _get_json(self, url: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        # retry klein & fein
        for attempt in range(3):
            try:
                async with self._session.get(url, headers=self._headers(), params=params, timeout=20) as resp:
                    if resp.status == 401:
                        raise ShlinkApiError("Unauthorized (API key?)")
                    if resp.status >= 400:
                        text = await resp.text()
                        raise ShlinkApiError(f"HTTP {resp.status}: {text[:200]}")
                    return await resp.json()
            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                if attempt == 2:
                    raise ShlinkApiError(str(e))
                await asyncio.sleep(0.5 * (attempt + 1))
        raise ShlinkApiError("Unexpected")

    async def get_general_visits(self) -> Dict[str, Any]:
        """
        GET /rest/v{version}/visits
        Erwartete Felder (typisch): {"visits": {"total": <int>, "orphan": <int>, "nonOrphan": <int>, ...}}
        Falls dein Shlink leicht anders antwortet, mappen wir robust.
        """
        url = self._url("/visits")
        data = await self._get_json(url)
        return data

    async def get_orphan_visits_count(self) -> int:
        """
        GET /rest/v{version}/visits/orphan (paginiert)
        Wir laufen Seiten durch und zählen totalItems, falls vorhanden – oder len(items).
        """
        path = "/visits/orphan"
        page = 1
        per_page = 100
        total_count = 0
        total_items_reported: Optional[int] = None

        while True:
            url = self._url(path)
            params = {"page": page, "itemsPerPage": per_page}
            data = await self._get_json(url, params=params)

            # Shlink liefert meist "visits" + "pagination": {"totalItems": X, "pagesCount": Y, ...}
            visits = data.get("visits", [])
            pagination = data.get("pagination") or data.get("meta", {}).get("pagination")
            if pagination and "totalItems" in pagination:
                total_items_reported = int(pagination["totalItems"])
                break

            total_count += len(visits)

            if pagination:
                current = pagination.get("currentPage") or page
                pages = pagination.get("pagesCount")
                if pages and current >= pages:
                    break
            else:
                # keine Pagination -> eine Seite
                break

            page += 1

        return int(total_items_reported) if total_items_reported is not None else total_count

    async def get_short_url_count(self) -> int:
        """
        GET /rest/v{version}/short-urls (paginiert)
        Lies pagination.totalItems, sonst Seitenweise zählen.
        """
        path = "/short-urls"
        page = 1
        per_page = 100
        total_items_reported: Optional[int] = None
        manual_count = 0

        while True:
            url = self._url(path)
            params = {"page": page, "itemsPerPage": per_page}
            data = await self._get_json(url, params=params)

            pagination = data.get("pagination") or data.get("meta", {}).get("pagination")
            short_urls = data.get("shortUrls") or data.get("data") or []

            if pagination and "totalItems" in pagination:
                total_items_reported = int(pagination["totalItems"])
                break

            manual_count += len(short_urls)

            if pagination:
                current = pagination.get("currentPage") or page
                pages = pagination.get("pagesCount")
                if pages and current >= pages:
                    break
            else:
                break

            page += 1

        return int(total_items_reported) if total_items_reported is not None else manual_count

    async def get_non_orphan_visits_count(self) -> int:
        """
        Nutze die Gesamt-Stats und ziehe Orphans ab, falls Feld vorhanden.
        Fallback: GET /visits (total) – orphan -> nonOrphan
        """
        stats = await self.get_general_visits()
        visits = stats.get("visits") or stats  # robustes Mapping
        total = int(visits.get("total") or 0)
        orphan = int(visits.get("orphan") or visits.get("orphanVisits", 0))
        non_orphan = visits.get("nonOrphan")
        if non_orphan is not None:
            return int(non_orphan)
        if total and orphan:
            return max(0, total - orphan)
        # harter Fallback: Wenn nur orphan bekannt ist, zähle non-orphan via gesondertem Endpunkt, falls vorhanden
        # einige Shlink-Versionen bieten /visits/non-orphan:
        try:
            data = await self._get_json(self._url("/visits/non-orphan"))
            # analoges Schema wie orphan
            pagination = data.get("pagination") or data.get("meta", {}).get("pagination")
            if pagination and "totalItems" in pagination:
                return int(pagination["totalItems"])
            return len(data.get("visits", []))
        except ShlinkApiError:
            return 0