"""Platform for sensor integration."""
from __future__ import annotations
import aiohttp
import async_timeout
import logging
import base64
from datetime import timedelta
from typing import Set

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
        self._known_docs: Set[int] = set()
        self._protocol = "https" if ssl else "http"
        self._base_url = f"{self._protocol}://{self._host}:{self._port}"

    async def _get_document_preview(self, doc_id: int) -> str | None:
        """Fetch document preview image."""
        url = f"{self._base_url}/api/documents/{doc_id}/preview/"
        headers = {
            "Authorization": f"Token {self._token}",
        }
        
        try:
            async with async_timeout.timeout(10):
                async with self._session.get(url, headers=headers) as response:
                    if response.status == 200:
                        image_data = await response.read()
                        return base64.b64encode(image_data).decode('utf-8')
        except Exception as err:
            _LOGGER.error("Error fetching preview for document %s: %s", doc_id, err)
        return None

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    async def async_update(self) -> None:
        """Fetch new state data for the sensor."""
        url = f"{self._base_url}/api/documents/"
        
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
                        documents = data.get("results", [])
                        current_doc_ids = {doc["id"] for doc in documents}
                        
                        # Finde neue Dokumente
                        new_doc_ids = current_doc_ids - self._known_docs
                        if new_doc_ids and self._known_docs:  # Ignoriere beim ersten Start
                            for doc_id in new_doc_ids:
                                doc = next((d for d in documents if d["id"] == doc_id), None)
                                if doc:
                                    preview = await self._get_document_preview(doc_id)
                                    
                                    # Event auslösen
                                    self.hass.bus.async_fire("paperless_new_document", {
                                        "document_id": doc_id,
                                        "title": doc.get("title", "Unbekanntes Dokument"),
                                        "created": doc.get("created"),
                                        "preview": preview
                                    })
                                    
                                    # Benachrichtigung senden
                                    message = f"Neues Dokument: {doc.get('title', 'Unbekanntes Dokument')}"
                                    if preview:
                                        message += f"\n\n![Vorschau](data:image/png;base64,{preview})"
                                    
                                    await self.hass.services.async_call(
                                        "persistent_notification",
                                        "create",
                                        {
                                            "title": "Neues Paperless Dokument",
                                            "message": message,
                                            "notification_id": f"paperless_new_doc_{doc_id}"
                                        }
                                    )
                        
                        self._known_docs = current_doc_ids
                        self._attr_extra_state_attributes["documents_count"] = len(documents)
                        self._attr_extra_state_attributes["last_error"] = None

                    elif response.status == 401:
                        self._attr_native_value = "Unauthorized"
                        self._attr_extra_state_attributes["last_error"] = "Invalid authentication token"
                    else:
                        self._attr_native_value = "Error"
                        self._attr_extra_state_attributes["last_error"] = f"HTTP {response.status}"
        except Exception as err:
            self._attr_native_value = "Error"
            self._attr_extra_state_attributes["last_error"] = str(err)
            _LOGGER.error("Unexpected error: %s", err)