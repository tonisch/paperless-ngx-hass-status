# Paperless Status Sensor für Home Assistant

## Installation

[![Open your Home Assistant instance and show the add add-on repository dialog with a specific repository URL pre-filled.](https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg)](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https://github.com/tonisch/paperless-ngx-hass-status)

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