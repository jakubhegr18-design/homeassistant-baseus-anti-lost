"""Data coordinator for the Baseus Anti-Lost T2 integration."""

from __future__ import annotations

import logging
import time
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    CONF_ADDRESS,
    CONF_OUT_OF_RANGE_TIMEOUT,
    CONF_RSSI_THRESHOLD,
    DEFAULT_OUT_OF_RANGE_TIMEOUT,
    DEFAULT_RSSI_THRESHOLD,
    DOMAIN,
    STATE_CONNECTED,
    STATE_DISCONNECTED,
    STATE_LOST,
    STATE_OUT_OF_RANGE,
    STATE_SAFE,
)

_LOGGER = logging.getLogger(__name__)

UPDATE_INTERVAL = timedelta(seconds=30)


class BaseusAntiLostCoordinator(DataUpdateCoordinator):
    """Coordinator polling the Anti-Lost T2 device over Bluetooth."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the coordinator."""
        self.entry = entry
        self.address: str = entry.data[CONF_ADDRESS]
        self.device_name: str = entry.title

        self.rssi_threshold: int = entry.options.get(
            CONF_RSSI_THRESHOLD, DEFAULT_RSSI_THRESHOLD
        )
        self.out_of_range_timeout: int = entry.options.get(
            CONF_OUT_OF_RANGE_TIMEOUT, DEFAULT_OUT_OF_RANGE_TIMEOUT
        )

        self.rssi: int | None = None
        self.battery_level: int | None = None
        self.connected: bool = False
        self.anti_lost_enabled: bool = True
        self.tracking: bool = False
        self.last_seen_ts: float | None = None
        self._last_connected_ts: float | None = None

        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{self.address}",
            update_interval=UPDATE_INTERVAL,
        )

    @property
    def device_info(self) -> dict:
        """Return device registry information."""
        from homeassistant.helpers.device_registry import CONNECTION_BLUETOOTH

        return {
            "identifiers": {(DOMAIN, self.address)},
            "connections": {(CONNECTION_BLUETOOTH, self.address)},
            "name": self.device_name,
            "manufacturer": "Baseus",
            "model": "Anti-Lost T2",
        }

    @property
    def is_available(self) -> bool:
        """Return whether the device is reachable."""
        return self.last_seen_ts is not None

    @property
    def is_connected(self) -> bool:
        """Return whether the device is currently connected."""
        return self.connected

    @property
    def is_lost(self) -> bool:
        """Return whether the device is considered lost."""
        return self.tracking_state in (STATE_OUT_OF_RANGE, STATE_LOST)

    @property
    def connection_state(self) -> str:
        """Return the connection state string."""
        return STATE_CONNECTED if self.connected else STATE_DISCONNECTED

    @property
    def tracking_state(self) -> str:
        """Compute the tracking state from the last-seen timestamp."""
        if self.last_seen_ts is None:
            return STATE_LOST
        elapsed = time.monotonic() - self.last_seen_ts
        if elapsed <= self.out_of_range_timeout:
            return STATE_SAFE
        return STATE_OUT_OF_RANGE

    @property
    def last_seen(self) -> int | None:
        """Return seconds since the device was last seen."""
        if self.last_seen_ts is None:
            return None
        return int(time.monotonic() - self.last_seen_ts)

    @property
    def distance_estimate(self) -> float | None:
        """Estimate distance in metres from the RSSI value."""
        if self.rssi is None:
            return None
        # Log-distance path loss model (n ~= 2.0 for free space)
        tx_power = -59
        if self.rssi == 0:
            return None
        ratio = self.rssi / tx_power
        if ratio < 1:
            return round(pow(ratio, 10), 2)
        return round(pow(ratio, 7.7095) * 0.89976 + 0.111, 2)

    async def _async_update_data(self) -> dict:
        """Poll the device over Bluetooth Low Energy."""
        try:
            await self._async_poll_device()
        except Exception as err:  # noqa: BLE001
            _LOGGER.debug("Error polling %s: %s", self.address, err)

        if self.connected:
            self.last_seen_ts = time.monotonic()
            self._last_connected_ts = self.last_seen_ts

        return {
            "rssi": self.rssi,
            "battery": self.battery_level,
            "connected": self.connected,
            "tracking": self.tracking_state,
            "last_seen": self.last_seen,
        }

    async def _async_poll_device(self) -> None:
        """Connect to the device and refresh its characteristics."""
        from bleak import BleakClient

        client = BleakClient(self.address, timeout=10.0)
        try:
            await client.connect()
            self.connected = client.is_connected
            self.rssi = getattr(client, "rssi", None)
            self.battery_level = await self._async_read_battery(client)
        finally:
            if client.is_connected:
                await client.disconnect()

    async def _async_read_battery(self, client) -> int | None:
        """Read the standard Bluetooth battery level characteristic."""
        from bleak.exc import BleakError

        battery_uuid = "00002a19-0000-1000-8000-00805f9b34fb"
        try:
            data = await client.read_gatt_char(battery_uuid)
            if data:
                return int(data[0])
        except (BleakError, ValueError, IndexError):
            return None
        return None

    async def async_send_command(self, command: str) -> None:
        """Send a tracking command to the device/service."""
        _LOGGER.info("Sending command %s to %s", command, self.address)
        if command == "start_tracking":
            self.tracking = True
        elif command == "stop_tracking":
            self.tracking = False

    async def async_shutdown(self) -> None:
        """Clean up resources when the entry is unloaded."""
        self.connected = False
