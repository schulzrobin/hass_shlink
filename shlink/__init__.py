from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

DOMAIN = "shlink"

async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the Shlink integration."""
    hass.data.setdefault(DOMAIN, {})
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up Shlink from a config entry."""
    hass.data[DOMAIN][entry.entry_id] = entry.data

    # Hier können Sensoren oder andere Plattformen initialisiert werden
    hass.config_entries.async_setup_platforms(entry, ["sensor"])
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a Shlink config entry."""
    hass.data[DOMAIN].pop(entry.entry_id)
    return await hass.config_entries.async_unload_platforms(entry, ["sensor"])