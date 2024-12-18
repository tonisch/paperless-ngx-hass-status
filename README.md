# Paperless Status Integration for Home Assistant

This integration provides a sensor for monitoring your Paperless-ngx instance and receiving notifications about new documents.

## Features

- Monitor the online status of your Paperless instance
- Track the total number of documents
- Receive notifications when new documents are added
- Preview images of new documents in notifications
- Easy configuration through the UI

## Installation

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=tonisch&repository=paperless-ngx-hass-status&category=integration)

1. Install HACS (Home Assistant Community Store)
2. Add this repository to HACS
3. Install the integration
4. Add the integration through the Home Assistant UI

## Configuration

### Through the UI
1. Go to Settings -> Devices & Services
2. Click the "+ ADD INTEGRATION" button
3. Search for "Paperless Status"
4. Fill in the required information:
   - Host: Your Paperless host (e.g., "localhost")
   - Port: Your Paperless port (default: 8000)
   - SSL: Enable if using HTTPS
   - Token: Your Paperless API token

### API Token
To get your API token:
1. Log in to your Paperless instance
2. Go to Settings -> Admin Interface
3. Navigate to "API Tokens"
4. Create a new token

## Notifications

The integration can notify you when new documents are added to Paperless. You can use these notifications in your automations:

```yaml
automation:
  - alias: "Paperless New Document Notification"
    trigger:
      platform: event
      event_type: paperless_new_document
    action:
      - service: notify.mobile_app_your_phone
        data_template:
          title: "New Paperless Document"
          message: "{{ trigger.event.data.title }}"
          data:
            image: "{{ trigger.event.data.preview }}"
```

### Available Event Data
- `document_id`: The ID of the new document
- `title`: The document's title
- `created`: Creation timestamp
- `preview`: Base64 encoded preview image

## Troubleshooting

If you experience issues:
1. Check if your Paperless instance is accessible
2. Verify your API token is valid
3. Check the Home Assistant logs for error messages

## Contributing

Feel free to contribute to this project by:
- Reporting issues
- Suggesting new features
- Creating pull requests

## License

This project is licensed under the MIT License - see the LICENSE file for details.

