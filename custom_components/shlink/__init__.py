from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN, PLATFORMS, CONF_BASE_URL, CONF_API_KEY, CONF_API_VERSION
from .api import ShlinkClient
from .coordinator import ShlinkCoordinator

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    base_url = entry.data[CONF_BASE_URL]
    api_key = entry.data[CONF_API_KEY]
    api_version = entry.data.get(CONF_API_VERSION, "3")

    client = ShlinkClient(base_url, api_key, api_version)
    coordinator = ShlinkCoordinator(hass, client)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "client": client,
        "coordinator": coordinator,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unloaded:
        data = hass.data[DOMAIN].pop(entry.entry_id)
        client: ShlinkClient = data["client"]
        await client.close()
    return unloaded