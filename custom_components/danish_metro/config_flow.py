"""Config flow for Danish Metro integration."""

from __future__ import annotations

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN


class DanishMetroConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Danish Metro."""

    VERSION = 1

    async def async_step_user(self, user_input=None) -> FlowResult:
        """Handle a flow initiated by the user."""
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        return self.async_create_entry(title="Danish Metro", data={})

    async def async_step_import(self, user_input=None) -> FlowResult:
        """Handle import from configuration.yaml."""
        return await self.async_step_user()
