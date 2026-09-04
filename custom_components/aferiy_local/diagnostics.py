from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .coordinator import AferiyLocalCoordinator


P280_KNOWN_MAPPINGS = {
    "R03": "Battery charge power (W)",
    "R06": "Total input power (W)",
    "R10": "DC output power / 10 (W)",
    "R18": "AC output voltage / 10 (V)",
    "R19": "AC frequency setting / 10 (Hz)",
    "R20": "AC output power (W)",
    "R21": "AC input voltage / 10 (V)",
    "R22": "AC input frequency / 100 (Hz)",
    "R34": "USB-C PD140 right power / 10 (W)",
    "R35": "USB-C PD140 left power / 10 (W)",
    "R36": "USB-C PD20 left power / 10 (W)",
    "R37": "USB-C PD20 right power / 10 (W)",
    "R39": "Total output power (W)",
    "R41": (
        "Output state flags: "
        "USB=0x0200, DC=0x0400, "
        "AC=0x0800, Light=0x1000"
    ),
    "R56": "Battery percentage / 10 (%)",
    "R58": "Time to full (minutes)",
    "R59": "Remaining time (minutes)",
}


P280_RESEARCH_CANDIDATES = {
    "R42": "Composite output configuration/state",
    "R47": "Stable configuration/status value",
    "R48": "Charging/input state candidate",
    "R53": "Unknown changing status value",
    "R54": "Unknown stable/status value",
    "R70": "SOC-related candidate",
    "R71": "SOC-related candidate",
}


P180_KNOWN_MAPPINGS = {
    "R02": "AC input power (W)",
    "R03": "Solar / DC input power (W)",
    "R08": "AC input voltage / 10 (V)",
    "R09": "AC input frequency / 100 (Hz)",
    "R10": "AC output voltage / 10 (V)",
    "R11": "AC frequency setting / 10 (Hz)",
    "R31": "Battery percentage (%)",
    "R71": "Time to full (minutes)",
    "R72": "Remaining time (minutes)",
    "R75": (
        "Output state flags: "
        "DC=0x0008, AC=0x0010"
    ),
    "R78": "DC output power (W)",
}


P180_RESEARCH_CANDIDATES = {
    "R12": "AC/output power channel candidate",
    "R13": "Battery/output power channel candidate",
    "R32": "Battery voltage candidate / 100 (V)",
    "R37": "Charging/state marker",
    "R39": "Charging/state marker",
    "R47": "Unknown configuration/status value",
    "R53": "Input/source state register",
    "R54": "DC-related register",
    "R60": "Unknown paired value with R61",
    "R61": "Unknown paired value with R60",
    "R66": "Unknown paired value with R67",
    "R67": "Unknown paired value with R66",
}


P180_PROFILE_MARKERS = {
    36,
    38,
    63,
}


def _register_name(
    register: int,
) -> str:
    return f"R{register:02d}"


def _format_registers_decimal(
    registers: dict[int, int],
) -> dict[str, int]:
    return {
        _register_name(register): value
        for register, value
        in sorted(registers.items())
    }


def _format_registers_hex(
    registers: dict[int, int],
) -> dict[str, str]:
    return {
        _register_name(register): (
            f"0x{value:04X}"
        )
        for register, value
        in sorted(registers.items())
    }


def _format_changed_registers(
    changes: dict[
        int,
        dict[str, int],
    ],
) -> dict[str, dict[str, Any]]:
    result: dict[
        str,
        dict[str, Any],
    ] = {}

    for register, values in sorted(
        changes.items()
    ):
        previous = values.get(
            "previous",
            0,
        )

        current = values.get(
            "current",
            0,
        )

        result[
            _register_name(register)
        ] = {
            "previous_decimal": (
                previous
            ),
            "current_decimal": (
                current
            ),
            "previous_hex": (
                f"0x{previous:04X}"
            ),
            "current_hex": (
                f"0x{current:04X}"
            ),
            "delta": (
                current - previous
            ),
        }

    return result


def _mapping_register_numbers(
    mappings: dict[str, str],
) -> set[int]:
    registers: set[int] = set()

    for name in mappings:
        if (
            len(name) == 3
            and name.startswith("R")
        ):
            try:
                registers.add(
                    int(name[1:])
                )
            except ValueError:
                pass

    return registers


def _interesting_unknown_registers(
    registers: dict[int, int],
    profile: str,
) -> dict[str, dict[str, Any]]:
    if profile == "p180_pro":
        known = _mapping_register_numbers(
            P180_KNOWN_MAPPINGS
        )

        candidates = (
            _mapping_register_numbers(
                P180_RESEARCH_CANDIDATES
            )
        )

        ignored = (
            known
            | candidates
            | P180_PROFILE_MARKERS
        )

    else:
        known = _mapping_register_numbers(
            P280_KNOWN_MAPPINGS
        )

        candidates = (
            _mapping_register_numbers(
                P280_RESEARCH_CANDIDATES
            )
        )

        ignored = (
            known
            | candidates
        )

    result: dict[
        str,
        dict[str, Any],
    ] = {}

    for register, value in sorted(
        registers.items()
    ):
        if register in ignored:
            continue

        if value == 0:
            continue

        result[
            _register_name(register)
        ] = {
            "decimal": value,
            "hex": f"0x{value:04X}",
        }

    return result


def _known_mappings(
    profile: str,
) -> dict[str, str]:
    if profile == "p180_pro":
        return dict(
            P180_KNOWN_MAPPINGS
        )

    return dict(
        P280_KNOWN_MAPPINGS
    )


def _research_candidates(
    profile: str,
) -> dict[str, str]:
    if profile == "p180_pro":
        return dict(
            P180_RESEARCH_CANDIDATES
        )

    return dict(
        P280_RESEARCH_CANDIDATES
    )


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> dict[str, Any]:
    coordinator: AferiyLocalCoordinator = (
        hass.data[
            DOMAIN
        ][entry.entry_id]
    )

    data = coordinator.data or {}

    profile = data.get(
        "device_profile",
        "unknown",
    )

    current_registers = (
        coordinator.last_registers
        or {}
    )

    previous_registers = (
        coordinator.previous_registers
        or {}
    )

    register_changes = (
        coordinator.last_register_changes
        or {}
    )

    raw_packet = (
        coordinator.last_raw_packet
    )

    if raw_packet:
        raw_packet_hex = (
            raw_packet.hex(" ")
        )
    else:
        raw_packet_hex = None

    diagnostics = {
        "integration": (
            "AFERIY Local for Home Assistant"
        ),

        "mode": "read only",

        "bluetooth_name": (
            coordinator.last_device_name
        ),

        "device_profile": (
            profile
        ),

        "profile_candidate": (
            coordinator.last_profile_candidate
        ),

        "packet_length": (
            coordinator.last_packet_length
        ),

        "raw_packet_hex": (
            raw_packet_hex
        ),

        "parsed_values": dict(
            data
        ),

        "known_mappings": (
            _known_mappings(
                profile
            )
        ),

        "research_candidates": (
            _research_candidates(
                profile
            )
        ),

        "interesting_unknown_registers": (
            _interesting_unknown_registers(
                current_registers,
                profile,
            )
        ),

        "changed_registers_since_previous_poll": (
            _format_changed_registers(
                register_changes
            )
        ),

        "previous_registers_decimal": (
            _format_registers_decimal(
                previous_registers
            )
        ),

        "previous_registers_hex": (
            _format_registers_hex(
                previous_registers
            )
        ),

        "registers_decimal": (
            _format_registers_decimal(
                current_registers
            )
        ),

        "registers_hex": (
            _format_registers_hex(
                current_registers
            )
        ),
    }

    if profile == "p180_pro":
        diagnostics[
            "p180_pro_debug"
        ] = {
            "battery_percent": (
                data.get(
                    "battery_percent"
                )
            ),

            "operating_mode": (
                data.get(
                    "operating_mode"
                )
            ),

            "charge_source": (
                data.get(
                    "charge_source"
                )
            ),

            "ac_input_power": (
                data.get(
                    "ac_input_power"
                )
            ),

            "solar_dc_input_power": (
                data.get(
                    "solar_dc_input_power"
                )
            ),

            "total_input_power": (
                data.get(
                    "total_input_power"
                )
            ),

            "ac_output_voltage": (
                data.get(
                    "ac_output_voltage"
                )
            ),

            "dc_output_power": (
                data.get(
                    "dc_output_power"
                )
            ),

            "total_output_power": (
                data.get(
                    "total_output_power"
                )
            ),

            "battery_discharge_power": (
                data.get(
                    "battery_discharge_power"
                )
            ),

            "remaining_minutes": (
                data.get(
                    "remaining_minutes"
                )
            ),

            "time_to_full": (
                data.get(
                    "time_to_full"
                )
            ),

            "ac_active": (
                data.get(
                    "ac_active"
                )
            ),

            "dc_active": (
                data.get(
                    "dc_active"
                )
            ),

            "battery_voltage_candidate": (
                data.get(
                    "battery_voltage_candidate"
                )
            ),

            "power_channel_1_r03": (
                data.get(
                    "power_channel_1"
                )
            ),

            "power_channel_2_r12": (
                data.get(
                    "power_channel_2"
                )
            ),

            "power_channel_3_r13": (
                data.get(
                    "power_channel_3"
                )
            ),

            "state_register_r75": (
                data.get(
                    "p180_state_register"
                )
            ),

            "dc_output_power_register_r78": (
                data.get(
                    "p180_dc_output_power_register"
                )
            ),

            "source_register_r53": (
                data.get(
                    "p180_source_register"
                )
            ),
        }

    return diagnostics
