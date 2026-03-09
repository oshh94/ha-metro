"""Config flow for Copenhagen Metro integration."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from homeassistant import config_entries

from .const import DOMAIN

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigFlowResult


class CopenhagenMetroConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Copenhagen Metro."""

    VERSION = 1

    async def async_step_user(
        self, _user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle a flow initiated by the user."""
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        return self.async_create_entry(title="Copenhagen Metro", data={})

    async def async_step_import(
        self, _user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle import from configuration.yaml."""
        return await self.async_step_user()
