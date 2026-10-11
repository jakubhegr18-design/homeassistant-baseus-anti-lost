"""Switch platform for the Baseus Anti-Lost T2 integration."""

from __future__ import annotations

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, SWITCH_ANTI_LOST
from .coordinator import BaseusAntiLostCoordinator
from .entity import BaseusAntiLostEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Baseus Anti-Lost T2 switch."""
    coordinator: BaseusAntiLostCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([BaseusAntiLostSwitch(coordinator)])


class BaseusAntiLostSwitch(BaseusAntiLostEntity, SwitchEntity):
    """Switch enabling or disabling anti-lost tracking."""

    _attr_translation_key = SWITCH_ANTI_LOST
    _attr_icon = "mdi:shield-check"

    def __init__(self, coordinator: BaseusAntiLostCoordinator) -> None:
        """Initialize the switch."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.address}_{SWITCH_ANTI_LOST}"

    @property
    def is_on(self) -> bool:
        """Return whether anti-lost tracking is enabled."""
        return self.coordinator.anti_lost_enabled

    async def async_turn_on(self, **kwargs) -> None:
        """Enable anti-lost tracking."""
        self.coordinator.anti_lost_enabled = True
        await self.coordinator.async_send_command("start_tracking")
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs) -> None:
        """Disable anti-lost tracking."""
        self.coordinator.anti_lost_enabled = False
        await self.coordinator.async_send_command("stop_tracking")
        self.async_write_ha_state()
