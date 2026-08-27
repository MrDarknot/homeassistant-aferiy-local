# AFERIY P280 for Home Assistant

Unofficial read only local Bluetooth integration for the AFERIY P280 power station.

## Features

The integration currently provides:

* Battery percentage
* Total input power
* Total output power
* Output power
* System power
* Remaining time
* Time to full
* AC output status
* DC output status
* USB output status
* Light status
* Bluetooth connection status

## Requirements

* Home Assistant with working Bluetooth
* AFERIY P280 within Bluetooth range
* No BrightEMS account required
* No cloud connection required

All communication is local over Bluetooth.

## Verified hardware

### AFERIY P280

Tested and verified.

Other AFERIY or BrightEMS based power stations may use a similar protocol, but are currently unverified.

## Installation with HACS

1. Open HACS
2. Go to Integrations
3. Open the menu
4. Select Custom repositories
5. Add this repository
6. Select Integration as the category
7. Install AFERIY P280
8. Restart Home Assistant

Then go to:

Settings → Devices & services → Add integration

Search for:

AFERIY P280

The integration will scan for compatible Bluetooth devices.

## Bluetooth

The P280 normally advertises using a name beginning with:

`POWER`

The Bluetooth MAC address is detected automatically and is not hardcoded.

## Privacy

The integration does not use the AFERIY cloud or BrightEMS cloud.

No AFERIY username or password is required.

## Status

Current release is read only.

Control of AC, DC and other power station functions is not currently included.

## Credits

Created by MrDarknot

BrightEMS protocol research based in part on ESP-FBot by Ylianst.

## Disclaimer

This is an unofficial community integration.

It is not affiliated with, endorsed by or supported by AFERIY or BrightEMS.

Use at your own risk.

## License

MIT License.
