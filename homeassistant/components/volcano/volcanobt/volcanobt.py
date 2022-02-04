"""Volcano BTLE implementation."""
import logging
import struct
from threading import Lock, Thread
import time

from .connection import BTLEConnection

_LOGGER = logging.getLogger(__name__)

VOLCANO_STAT_SERVICE_UUID = "10100000-5354-4f52-5a26-4249434b454c"
VOLCANO_HW_SERVICE_UUID = "10110000-5354-4f52-5a26-4249434b454c"

VOLCANO_TEMP_CURR_UUID = "10110001-5354-4f52-5a26-4249434b454c"
VOLCANO_TEMP_TARGET_UUID = "10110003-5354-4f52-5a26-4249434b454c"

VOLCANO_HEATER_ON_UUID = "1011000f-5354-4f52-5a26-4249434b454c"
VOLCANO_HEATER_OFF_UUID = "10110010-5354-4f52-5a26-4249434b454c"

VOLCANO_PUMP_ON_UUID = "10110013-5354-4f52-5a26-4249434b454c"
VOLCANO_PUMP_OFF_UUID = "10110014-5354-4f52-5a26-4249434b454c"

VOLCANO_AUTO_OFF_TIME_UUID = "1011000c-5354-4f52-5a26-4249434b454c"
VOLCANO_OPERATION_HOURS_UUID = "10110015-5354-4f52-5a26-4249434b454c"

VOLCANO_SERIAL_NUMBER_UUID = "10100008-5354-4f52-5a26-4249434b454c"
VOLCANO_FIRMWARE_VERSION_UUID = "10100003-5354-4f52-5a26-4249434b454c"
VOLCANO_BLE_FIRMWARE_VERSION_UUID = "10100004-5354-4f52-5a26-4249434b454c"

VOLCANO_STATUS_REGISTER_UUID = "1010000c-5354-4f52-5a26-4249434b454c"

VOLCANO_HEATER_ON_MASK = b"\x00\x20"
VOLCANO_PUMP_ON_MASK = b"\x20\x00"


class VolcanoBT(Thread):
    """Volcano BTLE implementation."""

    def __init__(self, _mac: str, _iface=None):
        """Initialize VolcanoBT."""
        Thread.__init__(self, daemon=True)

        self._temperature = 0
        self._target_temperature = 0
        self._heater_on = False
        self._pump_on = False
        self._auto_off_time = None
        self._operation_hours = None
        self._serial_number = None
        self._firmware_version = None
        self._ble_firmware_version = None
        self._lock = Lock()

        self.conn = BTLEConnection(_mac, _iface)
        self.conn.connect()
        self.stat_service = self.conn.get_service_by_uuid(VOLCANO_STAT_SERVICE_UUID)
        self.hw_service = self.conn.get_service_by_uuid(VOLCANO_HW_SERVICE_UUID)

    def run(self):
        """Run main notification loop."""
        while True:
            with self._lock:
                self.conn.wait_for_notifications(0.5)

            time.sleep(0.2)

    def initialize_values(self):
        """Initialize values from BT connection."""
        print("starting initialize values")

        self._temperature = self.read_temperature()
        self._target_temperature = self.read_target_temperature()

        self._auto_off_time = self.read_auto_off_time()
        self._operation_hours = self.read_operation_hours()

        self._serial_number = self.read_serial_number()
        self._firmware_version = self.read_firmware_version()
        # self._ble_firmware_version = self.read_ble_firmware_version()
        print("finishing initialize values")

    def register_notifications(self):
        """Register for BTLE gatt notifications."""
        print("starting register notifications")
        self.hw_service.get_characteristic(VOLCANO_TEMP_CURR_UUID).start_notify(
            self.temperature_changed
        )

        self.hw_service.get_characteristic(VOLCANO_TEMP_TARGET_UUID).start_notify(
            self.target_temperature_changed
        )

        self.stat_service.get_characteristic(VOLCANO_STATUS_REGISTER_UUID).start_notify(
            self.status_changed
        )
        print("finishing register notifications")

    @property
    def temperature(self):
        """Return Volcano temperature."""
        return self._temperature

    def temperature_changed(self, data):
        """Volcano temperature change callback."""
        temp = struct.unpack("<I", data)[0] / 10

        _LOGGER.debug("Temperature set to: %s", temp)

        self._temperature = round(temp)

    def read_temperature(self) -> int:
        """Read Volcano temperature from BTLE."""
        _LOGGER.debug("reading temperature")

        characteristic = self.hw_service.get_characteristic(VOLCANO_TEMP_CURR_UUID)

        _LOGGER.debug(characteristic)

        result = characteristic.read()

        return round(int(struct.unpack("<I", result)[0] / 10))

    @property
    def target_temperature(self):
        """Return Volcano target temperature."""
        return self._target_temperature

    @target_temperature.setter
    def target_temperature(self, temperature):
        """Volcano target temperature setter."""
        characteristic = self.hw_service.get_characteristic(VOLCANO_TEMP_TARGET_UUID)

        data = struct.pack("<I", temperature * 10)

        _LOGGER.debug("Setting temperature to: %s", temperature)

        with self._lock:
            characteristic.write(data)

        self._target_temperature = round(temperature)

    def target_temperature_changed(self, data):
        """Volcano target temperature changed callback."""
        temp = struct.unpack("<I", data)[0] / 10

        _LOGGER.debug("Temperature set to: %s", temp)

        self._target_temperature = round(temp)

    def read_target_temperature(self):
        """Read Volcano target temperature from BTLE."""
        _LOGGER.debug("reading target temperature")

        characteristic = self.hw_service.get_characteristic(VOLCANO_TEMP_TARGET_UUID)

        result = characteristic.read()

        return int(struct.unpack("<I", result)[0] / 10)

    @property
    def heater_on(self):
        """Return Volcano heater state."""
        return self._heater_on

    def toggle_heater(self):
        """Toggle Volcano heater state."""
        heater_uuid = (
            VOLCANO_HEATER_OFF_UUID if self.heater_on else VOLCANO_HEATER_ON_UUID
        )

        print("getting characteristic")

        characteristic = self.hw_service.get_characteristic(heater_uuid)

        print("acquiring lock")

        with self._lock:
            print("writing heater on request")

            characteristic.write(struct.pack("B", 0))

            print("wrote heater on request")

    @property
    def pump_on(self):
        """Return Volcano pump state."""
        return self._pump_on

    def toggle_pump(self):
        """Toggle Volcano pump state."""
        pump_uuid = VOLCANO_PUMP_OFF_UUID if self.pump_on else VOLCANO_PUMP_ON_UUID

        characteristic = self.hw_service.get_characteristic(pump_uuid)

        with self._lock:
            characteristic.write(struct.pack("B", 0))

    def read_serial_number(self):
        """Return Volcano serial number."""
        characteristic = self.stat_service.get_characteristic(
            VOLCANO_SERIAL_NUMBER_UUID
        )

        return characteristic.read().decode("utf-8")

    def read_firmware_version(self):
        """Return Volcano firmware version."""
        characteristic = self.stat_service.get_characteristic(
            VOLCANO_FIRMWARE_VERSION_UUID
        )

        return characteristic.read().decode("utf-8")

    def read_ble_firmware_version(self):
        """Return Volcano BLE firmware version."""
        characteristic = self.stat_service.get_characteristic(
            VOLCANO_BLE_FIRMWARE_VERSION_UUID
        )

        return characteristic.read().decode("utf-8")

    def read_auto_off_time(self):
        """Return Volcano auto off time."""
        characteristic = self.hw_service.get_characteristic(VOLCANO_AUTO_OFF_TIME_UUID)

        result = characteristic.read()

        _LOGGER.debug(result)

        return int(struct.unpack("H", result)[0])

    def read_operation_hours(self):
        """Read Volcano operation hours from BTLE."""
        characteristic = self.hw_service.get_characteristic(
            VOLCANO_OPERATION_HOURS_UUID
        )

        result = characteristic.read()

        _LOGGER.debug(result)

        return int(struct.unpack("<I", result)[0])

    def status_changed(self, resp):
        """Volcano status changed callback."""
        print("CONNECTION STATE UPDATE")
        data = int.from_bytes(resp, byteorder="little")

        heater_mask = int.from_bytes(VOLCANO_HEATER_ON_MASK, byteorder="big")
        pump_mask = int.from_bytes(VOLCANO_PUMP_ON_MASK, byteorder="big")

        if (data & heater_mask) == 0:
            self._heater_on = False
        else:
            self._heater_on = True

        if (data & pump_mask) == 0:
            self._pump_on = False
        else:
            self._pump_on = True
