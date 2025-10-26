# Hue Cleaner for Home Assistant

A Home Assistant custom component that automatically cleans up unused Philips Hue Entertainment Areas created by Philips TV Ambilight + Hue sync.

## What it does

This component solves the issue where Philips TVs with Ambilight + Hue sync create multiple "Entertainment area" configurations on your Hue Hub, eventually slowing down the sync performance. The component automatically detects and removes inactive entertainment areas that match the pattern created by Philips TVs.

## Features

- 🔍 Automatically detects Philips Hue Hub
- 🔑 Secure API key management with button press authentication
- 🧹 Cleans up inactive entertainment areas every 2 hours
- 📊 Provides statistics on cleaned areas
- ⚙️ Easy configuration through Home Assistant UI

## Installation

1. Install via HACS (Home Assistant Community Store)
2. Restart Home Assistant
3. Add the integration through the UI
4. Configure your Hue Hub IP address
5. Press the button on your Hue Hub when prompted
6. The component will start cleaning automatically

## Requirements

- Home Assistant 2023.1.0 or later
- Philips Hue Hub on the same network
- Philips TV with Ambilight + Hue sync capability

## Development

1. Open project in VS Code/Cursor and reopen in dev container
2. Press F5 to start Home Assistant with debugger, then open http://localhost:8123

## Support

For issues and feature requests, please visit the [GitHub repository](https://github.com/srescio/hue-cleaner-homeassistant).

## Credits

Based on the original [Hue Cleaner](https://github.com/srescio/hue-cleaner) desktop application by [Simone Rescio](https://simonerescio.it).
