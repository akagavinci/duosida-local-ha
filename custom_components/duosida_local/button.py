"""Start/stop charging buttons."""
from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import DuosidaCoordinator
from .entity import DuosidaEntity


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator: DuosidaCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [
            DuosidaButton(coordinator, "start_charging", "Start charging",
                          "mdi:play", "async_start_charging"),
            DuosidaButton(coordinator, "stop_charging", "Stop charging",
                          "mdi:stop", "async_stop_charging"),
        ]
    )


class DuosidaButton(DuosidaEntity, ButtonEntity):
    def __init__(
        self,
        coordinator: DuosidaCoordinator,
        key: str,
        name: str,
        icon: str,
        method: str,
    ) -> None:
        super().__init__(coordinator, key)
        self._attr_name = name
        self._attr_icon = icon
        self._method = method

    async def async_press(self) -> None:
        try:
            await getattr(self.coordinator, self._method)()
        except RuntimeError as err:
            raise HomeAssistantError(str(err)) from err
