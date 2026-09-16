"""Wallbox telemetry sensors."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    UnitOfElectricCurrent,
    UnitOfEnergy,
    UnitOfPower,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import DuosidaCoordinator
from .entity import DuosidaEntity
from .vendor.duosida_local import ChargerStatus


@dataclass(frozen=True, kw_only=True)
class DuosidaSensorDescription(SensorEntityDescription):
    value_fn: Callable[[ChargerStatus], float | str | None] = None  # type: ignore[assignment]


SENSORS: tuple[DuosidaSensorDescription, ...] = (
    DuosidaSensorDescription(
        key="charger_state",
        translation_key="charger_state",
        name="State",
        value_fn=lambda s: s.state.value,
    ),
    DuosidaSensorDescription(
        key="power",
        name="Power",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfPower.WATT,
        value_fn=lambda s: round(s.power, 1),
    ),
    DuosidaSensorDescription(
        key="current",
        name="Current",
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        value_fn=lambda s: round(s.current, 1),
    ),
    DuosidaSensorDescription(
        key="session_energy",
        name="Session energy",
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        value_fn=lambda s: round(s.session_energy, 3),
    ),
    DuosidaSensorDescription(
        key="total_energy",
        name="Total energy",
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        value_fn=lambda s: round(s.total_energy, 3),
    ),
    DuosidaSensorDescription(
        key="temperature",
        name="Temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        value_fn=lambda s: s.station_temperature,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator: DuosidaCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        DuosidaSensor(coordinator, description) for description in SENSORS
    )


class DuosidaSensor(DuosidaEntity, SensorEntity):
    entity_description: DuosidaSensorDescription

    def __init__(
        self, coordinator: DuosidaCoordinator, description: DuosidaSensorDescription
    ) -> None:
        super().__init__(coordinator, description.key)
        self.entity_description = description

    @property
    def native_value(self):
        status = self.coordinator.data
        if status is None:
            return None
        return self.entity_description.value_fn(status)
