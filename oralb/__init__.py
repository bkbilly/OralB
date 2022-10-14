"""Connect with OralB Toothbrush."""

import asyncio
import logging
import time

import bleak
from bleak_retry_connector import BleakClient, BLEDevice, establish_connection

_LOGGER = logging.getLogger(__name__)


class OralB:
    """Connects to OralB toothbrush to get information."""

    def __init__(self, ble_device: BLEDevice) -> None:
        """Initialize the class object."""
        self.ble_device = ble_device
        self._cached_services = None
        self.client = None
        self.name = "OralB"
        self.prev_time = 0

        self.result = {
            "brush_time": None,
            "battery": None,
            "status": None,
            "mode": None,
            "sector": None,
            "sector_time": None,
        }

    def set_ble_device(self, ble_device) -> None:
        self.ble_device = ble_device

    def disconnect(self) -> None:
        self.client = None
        self.ble_device = None

    async def connect(self) -> None:
        """Ensure connection to device is established."""
        if self.client and self.client.is_connected:
            return

        # Check again while holding the lock
        if self.client and self.client.is_connected:
            return
        _LOGGER.debug(f"{self.name}: Connecting; RSSI: {self.ble_device.rssi}")
        try:
            self.client = await establish_connection(
                BleakClient,
                self.ble_device,
                self.name,
                self._disconnected,
                cached_services=self._cached_services,
                ble_device_callback=lambda: self.ble_device,
            )
            _LOGGER.debug(f"{self.name}: Connected; RSSI: {self.ble_device.rssi}")
        except Exception:
            _LOGGER.debug(f"{self.name}: Error connecting to device")

    def _disconnected(self, client: BleakClient) -> None:
        """Disconnected callback."""
        _LOGGER.debug(
            f"{self.name}: Disconnected from device; RSSI: {self.ble_device.rssi}"
        )
        self.client = None

    async def gatherdata(self):
        """Connect to the OralB to get data."""
        if self.ble_device is None:
            return self.result
        if time.time() - self.prev_time < 1:
            return self.result
        self.prev_time = time.time()
        await self.connect()
        chars = {
            "a0f0ff08-5047-4d53-8208-4f72616c2d42": "time",
            "a0f0ff05-5047-4d53-8208-4f72616c2d42": "battery",
            "a0f0ff04-5047-4d53-8208-4f72616c2d42": "status",
            "a0f0ff07-5047-4d53-8208-4f72616c2d42": "mode",
            "a0f0ff09-5047-4d53-8208-4f72616c2d42": "sector",
        }
        statuses = {
            2: "IDLE",
            3: "RUN",
        }
        modes = {
            0: "OFF",
            1: "DAILY_CLEAN",
            7: "INTENSE",
            2: "SENSITIVE",
            4: "WHITEN",
            3: "GUM_CARE",
            6: "TONGUE_CLEAN",
        }
        sectors = {
            0: "SECTOR_1",
            1: "SECTOR_2",
            2: "SECTOR_3",
            3: "SECTOR_4",
            4: "SECTOR_5",
            5: "SECTOR_6",
            7: "SECTOR_7",
            8: "SECTOR_8",
            "FE": "LAST_SECTOR",
            "FF": "NO_SECTOR",
        }
        try:
            tasks = []
            for char, _ in chars.items():
                tasks.append(asyncio.create_task(self.client.read_gatt_char(char)))
            results = await asyncio.gather(*tasks)
            res_dict = dict(zip(chars.values(), results))

            self.result["brush_time"] = 60 * res_dict["time"][0] + res_dict["time"][1]
            self.result["battery"] = res_dict["battery"][0]
            self.result["status"] = statuses.get(res_dict["status"][0], "UNKNOWN")
            self.result["mode"] = modes.get(res_dict["mode"][0], "UNKNOWN")
            self.result["sector"] = sectors.get(res_dict["sector"][0], "UNKNOWN")
            self.result["sector_time"] = res_dict["sector"][1]
        except Exception:
            _LOGGER.debug(f"{self.name}: Not connected to device")

        return self.result


async def discover():
    """Start looking for a OralB toothbrush."""
    devices = await bleak.BleakScanner.discover()
    for device in devices:
        if device.name == "Oral-B Toothbrush":
            return device


async def main():
    """Run manually."""
    ble_device = await discover()
    _LOGGER.debug(ble_device)
    orlb = OralB(ble_device)
    while True:
        time.sleep(1)
        _LOGGER.debug(await orlb.gatherdata())


if __name__ == "__main__":
    asyncio.run(main())
