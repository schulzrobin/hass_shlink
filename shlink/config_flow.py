from homeassistant import config_entries
import voluptuous as vol
from homeassistant.core import callback

from . import DOMAIN

class ShlinkConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Shlink."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}
        if user_input is not None:
            base_url = user_input["base_url"]
            api_key = user_input["api_key"]

            # Hier könntest du die API testen, um Eingaben zu validieren.
            if not self._test_shlink_connection(base_url, api_key):
                errors["base"] = "cannot_connect"
            else:
                return self.async_create_entry(title="Shlink API", data=user_input)

        data_schema = vol.Schema({
            vol.Required("base_url"): str,
            vol.Required("api_key"): str
        })

        return self.async_show_form(step_id="user", data_schema=data_schema, errors=errors)

    async def async_step_import(self, user_input=None):
        """Handle import from YAML."""
        return await self.async_step_user(user_input)

    @staticmethod
    def _test_shlink_connection(base_url, api_key):
        """Test the connection to the Shlink API."""
        import requests
        try:
            headers = {"X-Api-Key": api_key}
            response = requests.get(f"{base_url}/rest/v2/short-urls", headers=headers)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False

class ShlinkOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle Shlink options."""

    def __init__(self, config_entry):
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        options_schema = vol.Schema({
            vol.Required("update_interval", default=self.config_entry.options.get("update_interval", 60)): int
        })

        return self.async_show_form(step_id="init", data_schema=options_schema)