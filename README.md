# AFERIY Local for Home Assistant

Unofficial read only local Bluetooth integration for AFERIY power stations in Home Assistant.

The integration communicates directly with the power station over Bluetooth. No AFERIY account, BrightEMS account or cloud connection is required.

## Features

### AFERIY P280

The integration currently provides:

* Battery percentage
* Battery charge power
* Total input power
* AC input voltage
* AC input frequency
* AC output voltage
* AC frequency
* AC output power
* DC output power
* USB-C PD140 left power
* USB-C PD140 right power
* USB-C PD20 left power
* USB-C PD20 right power
* Total output power
* Remaining time
* Time to full
* AC output status
* DC output status
* USB output status
* Light status
* Bluetooth connection status
* Home Assistant diagnostics support

USB-A power is included in Total output power, but the individual USB-A ports do not currently expose separate power measurements.

Battery percentage and Time to full have also been tested with an AFERIY expansion battery connected.

### AFERIY P180 Pro

Experimental support is included for the AFERIY P180 Pro.

Currently available P180 Pro data includes:

* Battery percentage
* Total input power
* Total output power
* AC output voltage
* AC output frequency
* Battery discharge power
* AC output status
* DC output status
* Bluetooth connection status
* Home Assistant diagnostics support

P180 Pro support is still experimental and some values may require additional verification.

## Requirements

* Home Assistant with working Bluetooth
* Compatible AFERIY power station within Bluetooth range
* No AFERIY account required
* No BrightEMS account required
* No cloud connection required

All communication is local over Bluetooth.

## Verified hardware

### AFERIY P280

Tested and verified.

The P280 has been tested both with and without an AFERIY expansion battery connected.

### AFERIY P180 Pro

Experimental support.

Bluetooth communication and several sensor values have been successfully tested, but the complete protocol mapping is still being investigated.

Other AFERIY or BrightEMS based power stations may use a similar Bluetooth protocol, but they are currently unverified.

Support for additional models can be investigated using the built in Home Assistant diagnostics function.

## Installation with HACS

1. Open HACS
2. Go to Integrations
3. Open the menu
4. Select Custom repositories
5. Add this repository:

`https://github.com/MrDarknot/homeassistant-aferiy-local`

6. Select Integration as the category
7. Install AFERIY Local
8. Restart Home Assistant

Then go to:

`Settings → Devices & services → Add integration`

Search for:

`AFERIY Local`

The integration will scan for compatible Bluetooth devices.

## Bluetooth

Compatible power stations may advertise over Bluetooth using a name beginning with:

`POWER`

The Bluetooth MAC address is detected automatically and is not hardcoded.

The integration domain is:

`aferiy_local`

## Diagnostics

The integration includes Home Assistant diagnostics support.

Diagnostics can be downloaded directly from the integration device page in Home Assistant.

The diagnostics information can help with troubleshooting and investigating support for additional AFERIY power station models.

Review diagnostics before sharing them publicly.

## Privacy

The integration communicates directly with the power station over Bluetooth.

It does not require the AFERIY cloud or BrightEMS cloud.

No AFERIY username or password is required.

No BrightEMS username or password is required.

Normal operation does not require an internet connection.

## Status

The current release is read only.

The integration monitors information reported by the power station.

Control of AC, DC, USB, lights and other power station functions is not currently included.

## Credits

Created by MrDarknot.

BrightEMS protocol research based in part on ESP FBot by Ylianst.

## Disclaimer

This is an unofficial community integration.

It is not affiliated with, endorsed by or supported by AFERIY or BrightEMS.

Use at your own risk.

## License

MIT License.
