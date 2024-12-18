"""Paperless-ngx Status Sensor für Home Assistant."""
from datetime import timedelta
import logging
import aiohttp
import voluptuous as vol

from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import (
    CONF_HOST,
    CONF_TOKEN,
    CONF_NAME,
    CONF_SCAN_INTERVAL
)
from homeassistant.helpers.entity import Entity
import homeassistant.helpers.config_validation as cv

_LOGGER = logging.getLogger(__name__)

DEFAULT_NAME = "Paperless Health"
DEFAULT_SCAN_INTERVAL = timedelta(minutes=5)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_HOST): cv.url,
    vol.Required(CONF_TOKEN): cv.string,
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): cv.time_period
})

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Richte den Paperless-Sensor ein."""
    name = config.get(CONF_NAME)
    host = config.get(CONF_HOST)
    token = config.get(CONF_TOKEN)

    async_add_entities([PaperlessHealthSensor(name, host, token)], True)

class PaperlessHealthSensor(Entity):
    """Sensor für den Paperless-ngx Gesundheitsstatus."""

    def __init__(self, name, host, token):
        self._name = name
        self._host = host.rstrip('/')
        self._token = token
        self._state = None
        self._attributes = {}

    @property
    def name(self):
        """Rückgabe des Sensornamens."""
        return self._name

    @property
    def state(self):
        """Rückgabe des Sensorstatus."""
        return self._state

    @property
    def extra_state_attributes(self):
        """Rückgabe der Sensorattribute."""
        return self._attributes

    async def async_update(self):
        """Hole die neuesten Daten von Paperless-ngx."""
        headers = {
            "Authorization": f"Token {self._token}"
        }

        try:
            async with aiohttp.ClientSession() as session:
                # Prüfe den Status-Endpunkt
                async with session.get(f"{self._host}/api/", headers=headers) as response:
                    if response.status == 200:
                        self._state = "online"
                        # Hole zusätzliche Statistiken
                        async with session.get(f"{self._host}/api/statistics/", headers=headers) as stats_response:
                            if stats_response.status == 200:
                                stats = await stats_response.json()
                                self._attributes = {
                                    "document_count": stats.get("document_count", 0),
                                    "inbox_count": stats.get("inbox_count", 0),
                                    "total_size": stats.get("total_size", 0)
                                }
                    else:
                        self._state = "offline"
        except Exception as err:
            _LOGGER.error("Fehler beim Abrufen von Paperless-ngx: %s", err)
            self._state = "error" 