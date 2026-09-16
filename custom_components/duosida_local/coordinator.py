"""Push coordinator holding the single persistent TCP session to the wallbox."""
from __future__ import annotations

import asyncio
import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN, RECONNECT_DELAY_S
from .vendor.duosida_local import ChargerStatus, DuosidaClient

_LOGGER = logging.getLogger(__name__)


class DuosidaCoordinator(DataUpdateCoordinator[ChargerStatus | None]):
    """Maintains connection, streams telemetry, exposes commands."""

    def __init__(self, hass: HomeAssistant, host: str, device_id: str) -> None:
        super().__init__(hass, _LOGGER, name=DOMAIN)
        self.host = host
        self.device_id = device_id
        self.model: str | None = None
        self.firmware: str | None = None
        self.requested_max_current: int | None = None
        self.connected = False
        self._client: DuosidaClient | None = None
        self._task: asyncio.Task | None = None

    def start(self) -> None:
        self._task = self.hass.loop.create_task(self._run())

    async def stop(self) -> None:
        if self._task:
            self._task.cancel()
            self._task = None
        await self._close_client()

    async def _close_client(self) -> None:
        if self._client:
            try:
                await self._client.disconnect()
            except Exception:  # noqa: BLE001 - best effort on teardown
                pass
            self._client = None
        self.connected = False

    async def _run(self) -> None:
        while True:
            try:
                client = DuosidaClient(self.host, timeout=20.0)
                await client.connect()
                self._client = client
                self.connected = True
                if self.model is None:
                    ident = await client.get_identity()
                    self.model = ident.model
                    self.firmware = ident.firmware
                _LOGGER.info("Duosida %s connected (%s)", self.host, self.model)
                self.async_set_updated_data(client.latest_status)
                async for status in client.states():
                    self.async_set_updated_data(status)
                _LOGGER.warning("Duosida telemetry stream ended")
            except asyncio.CancelledError:
                await self._close_client()
                raise
            except Exception as err:  # noqa: BLE001 - keep the loop alive
                _LOGGER.warning(
                    "Duosida connection error: %s — retrying in %ss",
                    err,
                    RECONNECT_DELAY_S,
                )
            await self._close_client()
            self.async_update_listeners()
            await asyncio.sleep(RECONNECT_DELAY_S)

    def _require_client(self) -> DuosidaClient:
        if self._client is None or not self.connected:
            raise RuntimeError("wallbox not connected")
        return self._client

    async def async_set_max_current(self, amps: int) -> None:
        await self._require_client().set_max_current(int(amps))
        self.requested_max_current = int(amps)
        self.async_update_listeners()

    async def async_start_charging(self) -> None:
        await self._require_client().start_charging()

    async def async_stop_charging(self) -> None:
        await self._require_client().stop_charging()
