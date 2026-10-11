"""Sensor platform for the Baseus Anti-Lost T2 integration."""

from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE,
    EntityCategory,
    UnitOfLength,
    UnitOfTime,
    SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    DOMAIN,
    SENSOR_BATTERY_LEVEL,
    SENSOR_CONNECTION_STATUS,
    SENSOR_DISTANCE_ESTIMATE,
    SENSOR_LAST_SEEN,
    SENSOR_SIGNAL_STRENGTH,
    SENSOR_TRACKING_STATUS,
)
from .coordinator import BaseusAntiLostCoordinator
from .entity import BaseusAntiLostEntity


@dataclass(frozen=True, kw_only=True)
class BaseusSensorDescription(SensorEntityDescription):
    """Describe a Baseus sensor entity."""

    value_fn: Callable[[BaseusAntiLostCoordinator], object]


SENSORS: tuple[BaseusSensorDescription, ...] = (
    BaseusSensorDescription(
        key=SENSOR_BATTERY_LEVEL,
        translation_key=SENSOR_BATTERY_LEVEL,
        device_class=SensorDeviceClass.BATTERY,
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda c: c.battery_level,
    ),
    BaseusSensorDescription(
        key=SENSOR_SIGNAL_STRENGTH,
        translation_key=SENSOR_SIGNAL_STRENGTH,
        device_class=SensorDeviceClass.SIGNAL_STRENGTH,
        native_unit_of_measurement=SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda c: c.rssi,
    ),
    BaseusSensorDescription(
        key=SENSOR_CONNECTION_STATUS,
        translation_key=SENSOR_CONNECTION_STATUS,
        icon="mdi:bluetooth",
        value_fn=lambda c: c.connection_state,
    ),
    BaseusSensorDescription(
        key=SENSOR_TRACKING_STATUS,
        translation_key=SENSOR_TRACKING_STATUS,
        icon="mdi:crosshairs-gps",
        value_fn=lambda c: c.tracking_state,
    ),
    BaseusSensorDescription(
        key=SENSOR_LAST_SEEN,
        translation_key=SENSOR_LAST_SEEN,
        device_class=SensorDeviceClass.TIMESTAMP,
        native_unit_of_measurement=UnitOfTime.SECONDS,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda c: _last_seen_ts(c),
    ),
    BaseusSensorDescription(
        key=SENSOR_DISTANCE_ESTIMATE,
        translation_key=SENSOR_DISTANCE_ESTIMATE,
        icon="mdi:map-marker-distance",
        native_unit_of_measurement=UnitOfLength.METERS,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda c: c.distance_estimate,
    ),
)


def _last_seen_ts(coordinator: BaseusAntiLostCoordinator) -> datetime | None:
    """Return the timestamp the device was last seen."""
    if coordinator.last_seen_ts is None:
        return None
    delta = time.monotonic() - coordinator.last_seen_ts
    return datetime.now(timezone.utc) - timedelta(seconds=delta)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Baseus Anti-Lost T2 sensors."""
    coordinator: BaseusAntiLostCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        BaseusAntiLostSensor(coordinator, description) for description in SENSORS
    )


class BaseusAntiLostSensor(BaseusAntiLostEntity, SensorEntity):
    """Representation of a Baseus Anti-Lost T2 sensor."""

    entity_description: BaseusSensorDescription

    def __init__(
        self,
        coordinator: BaseusAntiLostCoordinator,
        description: BaseusSensorDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.address}_{description.key}"

    @property
    def native_value(self) -> object:
        """Return the current value."""
        return self.entity_description.value_fn(self.coordinator)
