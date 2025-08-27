from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN, CONF_BASE_URL, CONF_API_KEY, CONF_API_VERSION
from .api import ShlinkClient, ShlinkApiError

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_BASE_URL): str,  # z.B. https://shlink.example.com
        vol.Required(CONF_API_KEY): str,
        vol.Optional(CONF_API_VERSION, default="3"): vol.In(["2", "3", "4"]),
    }
)

class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None) -> FlowResult:
        errors = {}
        if user_input is not None:
            # Testverbindung
            client = ShlinkClient(
                base_url=user_input[CONF_BASE_URL],
                api_key=user_input[CONF_API_KEY],
                api_version=user_input.get(CONF_API_VERSION, "3"),
            )
            try:
                await client.get_short_url_count()
                return self.async_create_entry(title="Shlink", data=user_input)
            except ShlinkApiError:
                errors["base"] = "cannot_connect"
            finally:
                await client.close()

        return self.async_show_form(step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors)