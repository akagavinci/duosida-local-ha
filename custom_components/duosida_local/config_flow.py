"""Config flow: host + connection test."""
from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_HOST

from .const import DEFAULT_HOST, DOMAIN
from .vendor.duosida_local import DuosidaClient, DuosidaError

STEP_USER_SCHEMA = vol.Schema({vol.Required(CONF_HOST, default=DEFAULT_HOST): str})


class DuosidaLocalConfigFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            host = user_input[CONF_HOST].strip()
            client = DuosidaClient(host, timeout=20.0)
            try:
                await client.connect()
                ident = await client.get_identity()
            except (DuosidaError, OSError, TimeoutError):
                errors["base"] = "cannot_connect"
            else:
                await self.async_set_unique_id(ident.device_id)
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=f"Duosida {ident.model}", data={CONF_HOST: host}
                )
            finally:
                try:
                    await client.disconnect()
                except Exception:  # noqa: BLE001
                    pass
        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_SCHEMA, errors=errors
        )
