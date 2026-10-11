"""Base entity for the Baseus Anti-Lost T2 integration."""

from __future__ import annotations

from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .coordinator import BaseusAntiLostCoordinator
from .const import DOMAIN


class BaseusAntiLostEntity(CoordinatorEntity[BaseusAntiLostCoordinator]):
    """Base class for all Baseus Anti-Lost T2 entities."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: BaseusAntiLostCoordinator) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)
        self._attr_device_info = coordinator.device_info

    @property
    def available(self) -> bool:
        """Return whether the entity is available."""
        return self.coordinator.is_available or self.coordinator.is_connected
