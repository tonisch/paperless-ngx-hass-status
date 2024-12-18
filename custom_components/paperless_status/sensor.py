"""Platform for sensor integration."""
from __future__ import annotations
import asyncio
import aiohttp
import async_timeout
import logging
from datetime import timedelta

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.const import (
    CONF_HOST,
    CONF_PORT,
    CONF_SSL,
    CONF_TOKEN,
)
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.util import Throttle

_LOGGER = logging.getLogger(__name__)
MIN_TIME_BETWEEN_UPDATES = timedelta(seconds=60)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    host = config_entry.data[CONF_HOST]
    port = config_entry.data[CONF_PORT]
    ssl = config_entry.data[CONF_SSL]
    token = config_entry.data[CONF_TOKEN]
    
    async_add_entities([PaperlessStatusSensor(hass, host, port, ssl, token)], True)

class PaperlessStatusSensor(SensorEntity):
    """Representation of a Paperless Status Sensor."""

    def __init__(self, hass: HomeAssistant, host: str, port: int, ssl: bool, token: str) -> None:
        """Initialize the sensor."""
        self.hass = hass
        self._host = host
        self._port = port
        self._ssl = ssl
        self._token = token
        self._attr_name = "Paperless Status"
        self._attr_unique_id = f"paperless_status_{host}_{port}"
        self._attr_native_value = "Unknown"
        self._attr_extra_state_attributes = {
            "documents_count": 0,
            "last_error": None
        }
        self._session = async_get_clientsession(hass)

    @property
    def icon(self):
        """Icon to use in the frontend."""
        if self._attr_native_value == "Online":
            return "mdi:file-document-multiple"
        return "mdi:file-document-multiple-outline"

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    async def async_update(self) -> None:
        """Fetch new state data for the sensor."""
        protocol = "https" if self._ssl else "http"
        url = f"{protocol}://{self._host}:{self._port}/api/documents/"
        
        headers = {
            "Authorization": f"Token {self._token}",
            "Content-Type": "application/json"
        }

        try:
            async with async_timeout.timeout(10):
                async with self._session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        self._attr_native_value = "Online"
                        self._attr_extra_state_attributes["documents_count"] = data.get("count", 0)
                        self._attr_extra_state_attributes["last_error"] = None
                    elif response.status == 401:
                        self._attr_native_value = "Unauthorized"
                        self._attr_extra_state_attributes["last_error"] = "Invalid authentication token"
                    else:
                        self._attr_native_value = "Error"
                        self._attr_extra_state_attributes["last_error"] = f"HTTP {response.status}"
        except aiohttp.ClientError as err:
            self._attr_native_value = "Offline"
            self._attr_extra_state_attributes["last_error"] = str(err)
            _LOGGER.error("Error connecting to Paperless: %s", err)
        except asyncio.TimeoutError:
            self._attr_native_value = "Timeout"
            self._attr_extra_state_attributes["last_error"] = "Connection timeout"
            _LOGGER.error("Timeout connecting to Paperless")
        except Exception as err:
            self._attr_native_value = "Error"
            self._attr_extra_state_attributes["last_error"] = str(err)
            _LOGGER.error("Unexpected error: %s", err)