![AFERIY Local for Home Assistant](https://github.com/MrDarknot/homeassistant-aferiy-local/raw/main/custom_components/aferiy_local/images/aferiy-banner.png)

<h1 align="center">AFERIY Local for Home Assistant</h1>

<p align="center">
  Local Bluetooth monitoring for AFERIY power stations in Home Assistant.
</p>

<p align="center">

![HACS Custom](https://img.shields.io/badge/HACS-Custom-41BDF5?logo=homeassistant&logoColor=white)
![Latest Release](https://img.shields.io/github/v/release/MrDarknot/homeassistant-aferiy-local?include_prereleases)
![Home Assistant](https://img.shields.io/badge/Home%20Assistant-2026.8.0%2B-41BDF5?logo=homeassistant&logoColor=white)
![License](https://img.shields.io/github/license/MrDarknot/homeassistant-aferiy-local)
![Read Only](https://img.shields.io/badge/Mode-Read%20Only-orange)
![Bluetooth](https://img.shields.io/badge/Connection-Local%20Bluetooth-blue)
[![Buy Me a Coffee](https://img.shields.io/badge/Buy%20Me%20a%20Coffee-Support%20me-FFDD00?logo=buymeacoffee&logoColor=000000)](https://buymeacoffee.com/mrdarknot)

</p>

AFERIY Local is an unofficial read only Home Assistant integration for compatible AFERIY power stations.

The integration communicates directly with the power station over Bluetooth.

No AFERIY account, BrightEMS account or cloud connection is required.

## Supported models

| Model | Support status |
|---|---|
| AFERIY P280 | ✅ Tested and verified |
| AFERIY P280 with expansion battery | ✅ Tested and verified |
| AFERIY P180 Pro | ✅ Tested and verified |
| AFERIY P180 Pro with expansion battery | ✅ Tested and verified |
| Other AFERIY models | ❓ Not yet verified |

## AFERIY P280

The P280 currently provides:

### Battery

* Battery percentage
* Battery charge power
* Remaining time
* Time to full

Battery percentage and Time to full have also been tested with an AFERIY expansion battery connected.

### Input

* Total input power
* AC input voltage
* AC input frequency

### AC output

* AC output voltage
* AC frequency
* AC output power
* AC output status

### DC output

* DC output power
* DC output status

### USB C output

Individual power measurements are available for:

* USB C PD140 left
* USB C PD140 right
* USB C PD20 left
* USB C PD20 right

### USB A output

USB A power is included in Total output power.

The individual USB A ports do not currently appear to expose separate power measurements.

### Other

* Operating mode
* Charge source
* Total output power
* USB output status
* Light status
* Bluetooth connection status
* Home Assistant diagnostics support

## AFERIY P180 Pro

Experimental support is included for the AFERIY P180 Pro.

Current sensor support includes:

### Battery

* Battery percentage
* Battery discharge power
* Remaining time
* Time to full

### Input

* AC input power
* Solar / DC input power
* Total input power
* AC input voltage
* AC input frequency

Total input power is calculated as:

`AC input power + Solar / DC input power`

This allows simultaneous AC and Solar / DC charging to be reported correctly.

### AC output

* AC output voltage
* AC frequency
* Total output power
* Output power
* AC output status

### DC output

* DC output power
* DC output status

Total output power combines AC output power and DC output power.

### Other

* Operating mode
* Charge source
* Bluetooth connection status
* Home Assistant diagnostics support

The P180 Pro now has broad read-only support, including battery status, AC input, Solar / DC input, AC and DC output information, remaining runtime, charging time, output states, Operating mode and Charge source.

Most currently exposed P180 Pro read-only sensors have been validated through controlled hardware testing and comparison with the P180 Pro display.

Operating mode and Charge source are derived from the validated sensor values.

P180 Pro support is still considered experimental, and some individual output power mappings may be refined as additional testing is completed.

## Requirements

* Home Assistant 2026.8.0 or newer
* Working Bluetooth support in Home Assistant
* Compatible AFERIY power station within Bluetooth range
* HACS for recommended installation

No AFERIY account is required.

No BrightEMS account is required.

No cloud connection is required.

All communication is local over Bluetooth.

## Installation with HACS

1. Open HACS
2. Go to Integrations
3. Open the menu
4. Select Custom repositories
5. Add this repository:

`https://github.com/MrDarknot/homeassistant-aferiy-local`

6. Select `Integration` as the category
7. Download `AFERIY Local`
8. Restart Home Assistant

Then go to:

`Settings → Devices & services → Add integration`

Search for:

`AFERIY Local`

The integration will scan for compatible Bluetooth devices.

## Bluetooth

Compatible power stations may advertise over Bluetooth using a name beginning with:

`POWER`

The Bluetooth address is discovered during setup and is not hardcoded.

The integration domain is:

`aferiy_local`

## Bluetooth recovery

The integration includes automatic Bluetooth recovery for stale BLE and GATT connections.

If a Bluetooth characteristic is missing or a status request times out, the integration can automatically:

* Clear the Bluetooth and GATT cache
* Close stale Bluetooth connections
* Perform a fresh active Bluetooth scan
* Retry the connection without cached service data

The recovery process performs a single controlled retry after clearing stale Bluetooth state.

This is intended to improve long-term Bluetooth stability and reduce the need for manual Home Assistant or integration restarts.

## Diagnostics

The integration includes extended diagnostics intended to help with testing and reverse engineering additional AFERIY models.

Diagnostics currently include:

* Known register mappings
* Research candidates
* Interesting unknown registers
* Registers changed since the previous poll
* Previous register values
* Current register values
* Decimal and hexadecimal register dumps
* Raw Bluetooth status packet
* Detected device profile

The diagnostics are read-only and do not send control commands to the power station.

This information can be especially useful when testing new AFERIY models or identifying previously unknown register mappings.

## Privacy

AFERIY Local communicates directly with the power station over Bluetooth.

The integration does not require:

* AFERIY Cloud
* BrightEMS Cloud
* AFERIY username or password
* BrightEMS username or password

Normal operation does not require an internet connection.

## Current status

AFERIY Local is currently read only.

The integration monitors information reported by supported power stations.

Direct control of AC, DC, USB, lights and charging settings is not currently included.

Bluetooth control may be investigated in future releases.

## Protocol research

The AFERIY Bluetooth protocol is not officially documented.

Support has been developed through direct Bluetooth communication, controlled testing and register comparison.

Testing data from other AFERIY models is welcome.

## Credits

Created by **MrDarknot**.

BrightEMS protocol research based in part on ESP FBot by Ylianst.

Thanks to community members helping test additional AFERIY hardware.

Special thanks to **FreezerHam** for helping test and validate AFERIY P180 Pro support.

## Disclaimer

This is an unofficial community integration.

It is not affiliated with, endorsed by or supported by AFERIY or BrightEMS.

Use at your own risk.

## License

MIT License.
