from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import ShlinkCoordinator

@dataclass
class SensorDescription:
    key: str
    name: str
    icon: str
    unit: str | None = None

SENSORS = [
    SensorDescription("short_url_count", "Shlink Shortlinks", "mdi:link-variant", None),
    SensorDescription("non_orphan_visits", "Shlink Visits", "mdi:eye", None),
    SensorDescription("orphan_visits", "Shlink Orphan Visits", "mdi:eye-off", None),
]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, add_entities: AddEntitiesCallback):
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator: ShlinkCoordinator = data["coordinator"]

    entities = [ShlinkSensor(coordinator, desc, entry.entry_id) for desc in SENSORS]
    add_entities(entities)

class ShlinkSensor(CoordinatorEntity[ShlinkCoordinator], SensorEntity):
    _attr_has_entity_name = True

    def __init__(self, coordinator: ShlinkCoordinator, desc: SensorDescription, entry_id: str):
        super().__init__(coordinator)
        self.entity_description = desc
        self._attr_name = desc.name
        self._attr_unique_id = f"shlink_{desc.key}_{entry_id}"
        self._attr_icon = desc.icon
        if desc.unit:
            self._attr_native_unit_of_measurement = desc.unit

    @property
    def native_value(self) -> Any:
        return self.coordinator.data.get(self.entity_description.key)