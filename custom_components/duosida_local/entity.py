"""Shared entity base."""
from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import DuosidaCoordinator


class DuosidaEntity(CoordinatorEntity[DuosidaCoordinator]):
    _attr_has_entity_name = True

    def __init__(self, coordinator: DuosidaCoordinator, key: str) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.device_id}_{key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.device_id)},
            name="Duosida Wallbox",
            manufacturer="Duosida",
            model=coordinator.model or "EV charger",
            sw_version=coordinator.firmware,
        )

    @property
    def available(self) -> bool:
        return self.coordinator.connected
