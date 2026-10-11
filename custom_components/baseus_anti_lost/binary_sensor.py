"""Binary sensor platform for the Baseus Anti-Lost T2 integration."""

from __future__ import annotations

from dataclasses import dataclass
from collections.abc import Callable

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    BINARY_SENSOR_BLUETOOTH_CONNECTED,
    BINARY_SENSOR_DEVICE_LOST,
    DOMAIN,
)
from .coordinator import BaseusAntiLostCoordinator
from .entity import BaseusAntiLostEntity


@dataclass(frozen=True, kw_only=True)
class BaseusBinarySensorDescription(BinarySensorEntityDescription):
    """Describe a Baseus binary sensor entity."""

    value_fn: Callable[[BaseusAntiLostCoordinator], bool]


BINARY_SENSORS: tuple[BaseusBinarySensorDescription, ...] = (
    BaseusBinarySensorDescription(
        key=BINARY_SENSOR_DEVICE_LOST,
        translation_key=BINARY_SENSOR_DEVICE_LOST,
        device_class=BinarySensorDeviceClass.PROBLEM,
        value_fn=lambda c: c.is_lost,
    ),
    BaseusBinarySensorDescription(
        key=BINARY_SENSOR_BLUETOOTH_CONNECTED,
        translation_key=BINARY_SENSOR_BLUETOOTH_CONNECTED,
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
        value_fn=lambda c: c.is_connected,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Baseus Anti-Lost T2 binary sensors."""
    coordinator: BaseusAntiLostCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        BaseusAntiLostBinarySensor(coordinator, description)
        for description in BINARY_SENSORS
    )


class BaseusAntiLostBinarySensor(BaseusAntiLostEntity, BinarySensorEntity):
    """Representation of a Baseus Anti-Lost T2 binary sensor."""

    entity_description: BaseusBinarySensorDescription

    def __init__(
        self,
        coordinator: BaseusAntiLostCoordinator,
        description: BaseusBinarySensorDescription,
    ) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.address}_{description.key}"

    @property
    def is_on(self) -> bool:
        """Return whether the binary sensor is on."""
        return bool(self.entity_description.value_fn(self.coordinator))
