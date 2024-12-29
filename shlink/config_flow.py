from homeassistant import config_entries
import voluptuous as vol

from . import DOMAIN

class ShlinkConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Shlink."""

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}
        if user_input is not None:
            # Validierung der Eingabe
            return self.async_create_entry(title="Shlink API", data=user_input)

        data_schema = vol.Schema({
            vol.Required("base_url"): str,
            vol.Required("api_key"): str
        })

        return self.async_show_form(step_id="user", data_schema=data_schema, errors=errors)