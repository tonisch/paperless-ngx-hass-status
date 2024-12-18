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

DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST, default="localhost"): vol.All(
            str,
            vol.Length(min=1),
            msg="Hostname oder IP-Adresse des Paperless-Servers"
        ),
        vol.Required(CONF_PORT, default=8000): vol.All(
            int,
            vol.Range(min=1, max=65535),
            msg="Port des Paperless-Servers (Standard: 8000)"
        ),
        vol.Required(CONF_SSL, default=False): vol.All(
            bool,
            msg="HTTPS für die Verbindung verwenden"
        ),
        vol.Required(CONF_TOKEN): vol.All(
            str,
            vol.Length(min=1),
            msg="API-Token aus den Paperless-Einstellungen"
        ),
    }
)

class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Paperless Status."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            return self.async_create_entry(
                title="Paperless Status",
                data=user_input
            )

        return self.async_show_form(
            step_id="user",
            data_schema=DATA_SCHEMA,
            errors=errors,
            description_placeholders={
                "token_help": "Den API-Token finden Sie in den Paperless-Einstellungen unter 'Admin Interface' → 'API-Tokens'",
            }
        ) 