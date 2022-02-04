"""Climate entity."""
from __future__ import annotations

from homeassistant.components.climate import ClimateEntity
from homeassistant.components.climate.const import (
    FAN_OFF,
    FAN_ON,
    HVAC_MODE_HEAT,
    HVAC_MODE_OFF,
    SUPPORT_AUX_HEAT,
    SUPPORT_FAN_MODE,
    SUPPORT_TARGET_TEMPERATURE,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_TEMPERATURE, PRECISION_WHOLE, TEMP_CELSIUS
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import Volcano, VolcanoEntity
from .const import DOMAIN

SUPPORT_FLAGS = SUPPORT_TARGET_TEMPERATURE | SUPPORT_AUX_HEAT | SUPPORT_FAN_MODE


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Minecraft Server sensor platform."""
    volcano = hass.data[DOMAIN][config_entry.unique_id]

    entities = [
        VolcanoThermostatEntity(volcano),
    ]

    async_add_entities(entities, True)


class VolcanoThermostatEntity(VolcanoEntity, ClimateEntity):
    """Volcano Thermostat entity class."""

    def __init__(self, volcano: Volcano) -> None:
        """Initialize VolcanoThermostatEntity."""
        super().__init__(volcano, "Volcano", "mdi:thermometer")

    @property
    def supported_features(self) -> int:
        """Return entity supported features."""
        return SUPPORT_FLAGS

    @property
    def available(self) -> bool:
        """Return entity availiability."""
        return True

    @property
    def should_poll(self) -> bool:
        """Return whether entity should poll."""
        return False

    @property
    def precision(self):
        """Return entity precision."""
        return PRECISION_WHOLE

    @property
    def temperature_unit(self):
        """Return entity temperature unit."""
        return TEMP_CELSIUS

    @property
    def current_temperature(self):
        """Return entity current temperature."""
        return self.volcano.conn.temperature

    @property
    def target_temperature(self):
        """Return entity target temperature."""
        return self.volcano.conn.target_temperature

    def set_temperature(self, **kwargs):
        """Set entity target temperature."""
        if (temperature := kwargs.get(ATTR_TEMPERATURE)) is None:
            return

        print(temperature)

        self.volcano.conn.target_temperature = round(temperature)

    @property
    def hvac_mode(self):
        """Return entity HVAC mode."""
        heater_on = self.volcano.conn.heater_on

        return HVAC_MODE_HEAT if heater_on else HVAC_MODE_OFF

    @property
    def hvac_modes(self):
        """Return entity HVAC modes."""
        return [HVAC_MODE_HEAT, HVAC_MODE_OFF]

    @property
    def fan_mode(self):
        """Return entity fan mode."""
        pump_on = self.volcano.conn.pump_on

        return FAN_ON if pump_on else FAN_OFF

    @property
    def fan_modes(self):
        """Return entity fan modes."""
        return [FAN_ON, FAN_OFF]

    @property
    def is_aux_heat(self):
        """Return entity auxiliary heat status."""
        return self.volcano.conn.heater_on

    @property
    def min_temp(self):
        """Return entity minimum temperature."""
        return 40

    @property
    def max_temp(self):
        """Return entity maximum temperature."""
        return 220
