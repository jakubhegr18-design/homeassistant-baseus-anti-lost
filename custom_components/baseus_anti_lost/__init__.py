"""The Baseus Anti-Lost T2 integration."""

from __future__ import annotations

import logging

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv
import homeassistant.helpers.device_registry as dr

from .const import (
    DOMAIN,
    SERVICE_RESET_DEVICE,
    SERVICE_START_TRACKING,
    SERVICE_STOP_TRACKING,
)
from .coordinator import BaseusAntiLostCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [
    Platform.BINARY_SENSOR,
    Platform.SENSOR,
    Platform.SWITCH,
]

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)

SERVICE_SCHEMA = vol.Schema({vol.Optional("device_id"): cv.string})


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the Baseus Anti-Lost T2 integration."""
    hass.data.setdefault(DOMAIN, {})

    async def _handle_command(call: ServiceCall, command: str) -> None:
        """Handle tracking services."""
        device_id = call.data.get("device_id")
        for entry_id, coordinator in hass.data[DOMAIN].items():
            if device_id is None or entry_id == device_id:
                await coordinator.async_send_command(command)

    async def async_start_tracking(call: ServiceCall) -> None:
        await _handle_command(call, "start_tracking")

    async def async_stop_tracking(call: ServiceCall) -> None:
        await _handle_command(call, "stop_tracking")

    async def async_reset_device(call: ServiceCall) -> None:
        await _handle_command(call, "reset_device")

    hass.services.async_register(
        DOMAIN, SERVICE_START_TRACKING, async_start_tracking, schema=SERVICE_SCHEMA
    )
    hass.services.async_register(
        DOMAIN, SERVICE_STOP_TRACKING, async_stop_tracking, schema=SERVICE_SCHEMA
    )
    hass.services.async_register(
        DOMAIN, SERVICE_RESET_DEVICE, async_reset_device, schema=SERVICE_SCHEMA
    )

    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Baseus Anti-Lost T2 from a config entry."""
    coordinator = BaseusAntiLostCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    entry.async_on_unload(entry.add_update_listener(async_reload_entry))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        coordinator: BaseusAntiLostCoordinator = hass.data[DOMAIN].pop(entry.entry_id)
        await coordinator.async_shutdown()
    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload the config entry when options change."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_migrate_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Migrate old config entries."""
    _LOGGER.debug("Migrating Baseus Anti-Lost T2 entry from version %s", entry.version)
    return True
