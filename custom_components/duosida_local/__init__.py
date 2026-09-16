"""Duosida Local integration."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, Platform
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .coordinator import DuosidaCoordinator

PLATFORMS = [Platform.SENSOR, Platform.NUMBER, Platform.BUTTON]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    coordinator = DuosidaCoordinator(
        hass, entry.data[CONF_HOST], entry.unique_id or entry.entry_id
    )
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    coordinator.start()
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    coordinator: DuosidaCoordinator = hass.data[DOMAIN].pop(entry.entry_id)
    await coordinator.stop()
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
