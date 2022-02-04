"""Platform for sensor integration."""
from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import TEMP_CELSIUS
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import Volcano, VolcanoEntity
from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Minecraft Server sensor platform."""
    volcano = hass.data[DOMAIN][config_entry.unique_id]

    entities = [
        VolcanoCurrentTemperatureSensor(volcano),
        VolcanoTargetTemperatureSensor(volcano),
    ]

    async_add_entities(entities, True)


class VolcanoSensorEntity(VolcanoEntity, SensorEntity):
    """Doc comment for sensor entity."""

    def __init__(
        self,
        volcano: Volcano,
        type_name: str,
        icon: str,
        unit: str,
        device_class: str = None,
    ) -> None:
        """Initialize entity."""
        super().__init__(volcano, type_name, icon, device_class)
        self._state = None
        self._unit = unit

    @property
    def available(self) -> bool:
        """Return entity availability."""
        return True

    @property
    def native_value(self) -> Any:
        """Return entity native value."""
        return self._state

    @property
    def should_poll(self) -> bool:
        """Return whether entity should poll."""
        return True

    @property
    def native_unit_of_measurement(self) -> str:
        """Return entity unit of measurement."""
        return self._unit


class VolcanoCurrentTemperatureSensor(VolcanoSensorEntity):
    """Representation of a Sensor."""

    def __init__(self, volcano: Volcano) -> None:
        """Initialize sensor base entity."""
        super().__init__(
            volcano=volcano,
            type_name="Current Temperature",
            icon="mdi:thermometer",
            unit=TEMP_CELSIUS,
        )

    def update(self) -> None:
        """Fetch new state data for the sensor."""
        self._state = self.volcano.conn.temperature


class VolcanoTargetTemperatureSensor(VolcanoSensorEntity):
    """Representation of a Sensor."""

    def __init__(self, volcano: Volcano) -> None:
        """Initialize sensor base entity."""
        super().__init__(
            volcano=volcano,
            type_name="Target Temperature",
            icon="mdi:thermometer",
            unit=TEMP_CELSIUS,
        )

    def update(self) -> None:
        """Fetch new state data for the sensor."""
        self._state = self.volcano.conn.target_temperature
