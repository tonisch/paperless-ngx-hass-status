"""Config flow for Paperless Status integration."""
from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import (
    CONF_HOST,
    CONF_PORT,
    CONF_SSL,
    CONF_TOKEN,
)

DOMAIN = "paperless_status"

class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Paperless Status."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(
                step_id="user",
                data_schema=vol.Schema(
                    {
                        vol.Required(CONF_HOST, default="localhost"): str,
                        vol.Required(CONF_PORT, default=8000): int,
                        vol.Required(CONF_SSL, default=False): bool,
                        vol.Required(CONF_TOKEN): str,
                    }
                )
            )

        return self.async_create_entry(
            title="Paperless Status",
            data=user_input
        ) 