from homeassistant.core import HomeAssistant

DOMAIN = "shlink"

async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the Shlink integration."""
    hass.data[DOMAIN] = {}
    return True

async def async_setup_entry(hass: HomeAssistant, entry):
    """Set up Shlink from a config entry."""
    hass.data[DOMAIN][entry.entry_id] = entry.data
    return True

async def async_unload_entry(hass: HomeAssistant, entry):
    """Unload a Shlink config entry."""
    hass.data[DOMAIN].pop(entry.entry_id)
    return True