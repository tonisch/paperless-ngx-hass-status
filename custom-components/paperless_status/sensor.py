
"""
Paperless-ngx Status Sensor for Home Assistant

This custom sensor integration checks the status of a Paperless-ngx Docker container
and provides various state attributes about its health and performance.

Installation:
1. Place this file in your Home Assistant configuration directory:
   <config_dir>/custom_components/paperless_status/sensor.py

2. Add configuration to configuration.yaml:
   sensor:
     - platform: paperless_status
       host: localhost
       port: 8000
       ssl: false
"""

import logging
from datetime import timedelta
import requests

import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from homeassistant.components.sensor import (
    SensorEntity,
    PLATFORM_SCHEMA
)
from homeassistant.const import (
    CONF_HOST, 
    CONF_PORT,
    CONF_SSL,
    STATE_UNAVAILABLE,
    STATE_RUNNING
)
from homeassistant.util import Throttle

_LOGGER = logging.getLogger(__name__)

# Configuration schema
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_HOST, default='localhost'): cv.string,
    vol.Required(CONF_PORT, default=8000): cv.port,
    vol.Optional(CONF_SSL, default=False): cv.boolean,
})

# Minimum time between updates
MIN_TIME_BETWEEN_UPDATES = timedelta(minutes=5)

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the Paperless status sensor."""
    host = config.get(CONF_HOST)
    port = config.get(CONF_PORT)
    use_ssl = config.get(CONF_SSL)

    add_entities([PaperlessSensor(host, port, use_ssl)], True)

class PaperlessSensor(SensorEntity):
    """Representation of a Paperless status sensor."""

    def __init__(self, host, port, use_ssl):
        """Initialize the sensor."""
        self._host = host
        self._port = port
        self._use_ssl = use_ssl
        self._state = STATE_UNAVAILABLE
        self._attributes = {}

    @property
    def name(self):
        """Return the name of the sensor."""
        return "Paperless Status"

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return self._attributes

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    def update(self):
        """Update sensor state and attributes."""
        try:
            # Construct base URL
            protocol = 'https' if self._use_ssl else 'http'
            base_url = f"{protocol}://{self._host}:{self._port}"

            # Check if Paperless is accessible
            response = requests.get(f"{base_url}/admin/", timeout=10)
            
            if response.status_code == 200:
                self._state = STATE_RUNNING
                
                # Additional status checks (mock data - replace with actual API calls if available)
                self._attributes = {
                    "documents_total": self._get_document_count(base_url),
                    "documents_untagged": self._get_untagged_document_count(base_url),
                    "storage_used": self._get_storage_usage(base_url)
                }
            else:
                self._state = STATE_UNAVAILABLE
                self._attributes = {}

        except (requests.ConnectionError, requests.Timeout) as err:
            _LOGGER.error(f"Could not connect to Paperless: {err}")
            self._state = STATE_UNAVAILABLE
            self._attributes = {}

    def _get_document_count(self, base_url):
        """Placeholder method to get total document count."""
        try:
            # Replace with actual API endpoint if available
            return 1000  # Mock data
        except Exception:
            return 0

    def _get_untagged_document_count(self, base_url):
        """Placeholder method to get untagged document count."""
        try:
            # Replace with actual API endpoint if available
            return 50  # Mock data
        except Exception:
            return 0

    def _get_storage_usage(self, base_url):
        """Placeholder method to get storage usage."""
        try:
            # Replace with actual API endpoint if available
            return "5.2 GB"  # Mock data
        except Exception:
            return "0 GB"
