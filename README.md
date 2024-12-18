# Paperless Status Sensor für Home Assistant

## Installation

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=tonisch&repository=paperless-ngx-hass-status&category=integration)

1. Installieren Sie HACS (Home Assistant Community Store)
2. Fügen Sie dieses Repository zu HACS hinzu
3. Installieren Sie die Integration
4. Konfigurieren Sie die Sensor-Optionen in Ihrer `configuration.yaml`

## Konfiguration

```yaml
sensor:
  - platform: paperless_status
    host: localhost
    port: 8000
    ssl: false