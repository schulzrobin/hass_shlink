from homeassistant.components.sensor import SensorEntity
from homeassistant.const import CONF_API_KEY, CONF_BASE_URL
import requests

from . import DOMAIN

class ShlinkSensor(SensorEntity):
    """Representation of a Shlink sensor."""

    def __init__(self, name, base_url, api_key):
        self._name = name
        self._base_url = base_url
        self._api_key = api_key
        self._state = None

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state

    def update(self):
        """Fetch new state data for the sensor."""
        headers = {"X-Api-Key": self._api_key}
        try:
            response = requests.get(f"{self._base_url}/rest/v2/short-urls", headers=headers)
            response.raise_for_status()
            data = response.json()
            self._state = len(data.get("shortUrls", []))
        except Exception as e:
            self._state = None
            print(f"Error fetching Shlink data: {e}")