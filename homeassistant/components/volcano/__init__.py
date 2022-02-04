"""The volcano integration."""
from __future__ import annotations

from typing import cast

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.typing import ConfigType

from .const import DOMAIN
from .volcanobt.volcanobt import (
    VOLCANO_STATUS_REGISTER_UUID,
    VOLCANO_TEMP_TARGET_UUID,
    VolcanoBT,
)

# For your initial PR, limit it to 1 platform.
PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.SWITCH, Platform.CLIMATE]


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Set up volcano from a config entry."""
    domain_data = hass.data.setdefault(DOMAIN, {})

    unique_id = config_entry.unique_id

    if not unique_id:
        return False

    volcano = Volcano(hass, unique_id, cast(ConfigType, config_entry.data))

    domain_data[unique_id] = volcano

    volcano.conn.start()

    hass.config_entries.async_setup_platforms(config_entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
    # hass.data[DOMAIN].pop(entry.entry_id)

    return True  # unload_ok


class Volcano:
    """Volcano bridge class."""

    def __init__(
        self, hass: HomeAssistant, unique_id: str, config_data: ConfigType
    ) -> None:
        """Initialize Volcano bridge class."""
        self._hass = hass

        self.unique_id = unique_id
        self.mac = config_data["mac"]
        self.conn = VolcanoBT(self.mac)
        self._stop_periodic_update = None

        self.conn.initialize_values()
        self.conn.register_notifications()


class VolcanoEntity(Entity):
    """Volcano entity class."""

    def __init__(
        self, volcano: Volcano, type_name: str, icon: str, device_class: str = None
    ) -> None:
        """Initialize base entity."""
        self.volcano = volcano
        self._name = f"Volcano {type_name}"
        self._icon = icon
        self._unique_id = f"{self.volcano.unique_id}-{type_name}"
        self._device_class = device_class
        self._more_notifications()

    def _more_notifications(self):
        status_char = self.volcano.conn.stat_service.get_characteristic(
            VOLCANO_STATUS_REGISTER_UUID
        )

        self.volcano.conn.conn.set_callback(status_char.handle, self._update_state)

        temp_char = self.volcano.conn.hw_service.get_characteristic(
            VOLCANO_TEMP_TARGET_UUID
        )

        self.volcano.conn.conn.set_callback(temp_char.handle, self._update_state)

    def _update_state(self, data):
        self.schedule_update_ha_state()

    @property
    def name(self) -> str:
        """Return entity name."""
        return self._name

    @property
    def unique_id(self) -> str:
        """Return entity unique id."""
        return self._unique_id

    @property
    def device_class(self) -> str:
        """Return entity device class."""
        return self._device_class if self._device_class else ""

    @property
    def icon(self) -> str:
        """Return entity icon."""
        return self._icon
