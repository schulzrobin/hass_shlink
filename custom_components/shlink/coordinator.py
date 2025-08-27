from __future__ import annotations

from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, COORDINATOR_UPDATE_INTERVAL
from .api import ShlinkClient, ShlinkApiError

class ShlinkCoordinator(DataUpdateCoordinator):
    def __init__(self, hass: HomeAssistant, client: ShlinkClient):
        super().__init__(
            hass,
            logger=hass.helpers.logger.LoggerAdapter(__name__),
            name=f"{DOMAIN}_coordinator",
            update_interval=timedelta(seconds=COORDINATOR_UPDATE_INTERVAL),
        )
        self.client = client

    async def _async_update_data(self):
        try:
            # Parallele Abfragen: Stats (für non-orphan) + orphan + short-url count
            non_orphan = await self.client.get_non_orphan_visits_count()
            orphan = await self.client.get_orphan_visits_count()
            short_count = await self.client.get_short_url_count()
            return {
                "non_orphan_visits": non_orphan,
                "orphan_visits": orphan,
                "short_url_count": short_count,
            }
        except ShlinkApiError as e:
            raise UpdateFailed(str(e)) from e