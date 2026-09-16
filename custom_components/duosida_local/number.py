"""Max charging current control."""
from __future__ import annotations

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfElectricCurrent
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, MAX_CURRENT_A, MIN_CURRENT_A
from .coordinator import DuosidaCoordinator
from .entity import DuosidaEntity


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator: DuosidaCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([DuosidaMaxCurrent(coordinator)])


class DuosidaMaxCurrent(DuosidaEntity, NumberEntity):
    _attr_name = "Max current"
    _attr_native_min_value = MIN_CURRENT_A
    _attr_native_max_value = MAX_CURRENT_A
    _attr_native_step = 1
    _attr_native_unit_of_measurement = UnitOfElectricCurrent.AMPERE
    _attr_mode = NumberMode.BOX
    _attr_icon = "mdi:current-ac"

    def __init__(self, coordinator: DuosidaCoordinator) -> None:
        super().__init__(coordinator, "max_current")

    @property
    def native_value(self) -> int | None:
        return self.coordinator.requested_max_current

    async def async_set_native_value(self, value: float) -> None:
        try:
            await self.coordinator.async_set_max_current(int(value))
        except RuntimeError as err:
            raise HomeAssistantError(str(err)) from err
