"""The bluetooth connection."""
import logging

from bluepy import btle

_LOGGER = logging.getLogger(__name__)


class BTLECharacteristic:
    """BTLE Characteristic class."""

    def __init__(self, characteristic):
        """Initialize BTLECharacteristic class."""
        self._characteristic = characteristic

    @property
    def handle(self) -> str:
        """Get characteristic handle."""
        return self._characteristic.getHandle()

    def start_notify(self, callback):
        """Fetch charactertic from handle and register gatt notifications."""
        _LOGGER.debug("Registering notification for handle %s", self.handle)

        descriptors = self._characteristic.getDescriptors("2902")

        if len(descriptors) != 1:
            raise Exception("CCCD descriptor not found")

        descriptors[0].write(b"\x01\x00")

        self._characteristic.peripheral.delegate.set_callback(self.handle, callback)

    def read(self):
        """Read gatt attribute."""
        return self._characteristic.read()

    def write(self, val):
        """Write gatt attribute."""
        return self._characteristic.peripheral.writeCharacteristic(self.handle, val)


class BTLEService:
    """BTLE Service class."""

    def __init__(self, service):
        """Initialize BTLEService."""
        self._service = service

    def get_characteristic(self, uuid):
        """Fetch characteristic from service."""
        characteristics = self._service.getCharacteristics(forUUID=uuid)

        if len(characteristics) != 1:
            raise Exception("Characteristic not found")

        return BTLECharacteristic(characteristics[0])


class BTLEConnection(btle.DefaultDelegate):
    """BTLE Connection class."""

    def __init__(self, mac, iface):
        """Initialize BTLEConnection."""
        btle.DefaultDelegate.__init__(self)
        self._conn = None
        self._mac = mac
        self._iface = iface
        self._callbacks = {}

    def connect(self):
        """Establish connection to device."""
        _LOGGER.debug("Connecting to bluetooth device")
        self._conn = btle.Peripheral()
        self._conn.withDelegate(self)

        _LOGGER.debug(self._mac)
        _LOGGER.debug(self._iface)

        try:
            self._conn.connect(
                self._mac, iface=self._iface, addrType=btle.ADDR_TYPE_RANDOM
            )
            _LOGGER.debug("Connected")
        except btle.BTLEException as ex:
            _LOGGER.debug(ex)

        return self

    def disconnect(self):
        """Disconnect from device."""
        if self._conn:
            self._conn.disconnect()
            self._conn = None

    def wait_for_notifications(self, *args):
        """Wait for BTLE notifications."""
        self._conn.waitForNotifications(args)

    def handleNotification(self, cHandle, data):
        """Iterate through registered callbacks when notification received."""
        _LOGGER.debug(cHandle)
        _LOGGER.debug(data)

        if cHandle in self._callbacks:
            for callback in self._callbacks[cHandle]:
                callback(data)

    def set_callback(self, handle, function):
        """Register callback for BTLE notification."""
        if handle not in self._callbacks:
            self._callbacks[handle] = []

        self._callbacks[handle].append(function)

    def get_service_by_uuid(self, uuid):
        """Get service by UUID."""
        try:
            return BTLEService(self._conn.getServiceByUUID(uuid))
        except btle.BTLEException as ex:
            _LOGGER.debug(ex)
