"""Platform for switch integration."""
from __future__ import annotations

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
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
        VolcanoHeaterSwitch(volcano),
        VolcanoPumpSwitch(volcano),
    ]

    async_add_entities(entities, True)


class VolcanoSwitchEntity(VolcanoEntity, SwitchEntity):
    """Representation of switch entity."""

    @property
    def available(self) -> bool:
        """Return entity availability."""
        return True


class VolcanoHeaterSwitch(VolcanoSwitchEntity):
    """Representation of a Sensor."""

    def __init__(self, volcano: Volcano) -> None:
        """Initialize sensor base entity."""
        super().__init__(
            volcano=volcano,
            type_name="Heater Switch",
            icon="mdi:radiator",
        )

    @property
    def is_on(self):
        """Return entity on state."""
        return self.volcano.conn.heater_on

    def turn_on(self, **kwargs):
        """Turn on entity heater."""
        print("TURN_ON")
        self.volcano.conn.toggle_heater()

    def turn_off(self, **kwargs):
        """Turn off entity heater."""
        self.volcano.conn.toggle_heater()

    def toggle(self, **kwargs) -> None:
        """Toggle entity heater state."""
        self.volcano.conn.toggle_heater()


class VolcanoPumpSwitch(VolcanoSwitchEntity):
    """Representation of a Sensor."""

    def __init__(self, volcano: Volcano) -> None:
        """Initialize sensor base entity."""
        super().__init__(
            volcano=volcano,
            type_name="Pump Switch",
            icon="mdi:pump",
        )

    @property
    def is_on(self):
        """Return entity on state."""
        return self.volcano.conn.pump_on

    def turn_on(self, **kwargs):
        """Turn on entity pump."""
        self.volcano.conn.toggle_pump()

    def turn_off(self, **kwargs):
        """Turn off entity pump."""
        self.volcano.conn.toggle_pump()

    def toggle(self, **kwargs):
        """Toggle entity pump state."""
        self.volcano.conn.toggle_pump()
