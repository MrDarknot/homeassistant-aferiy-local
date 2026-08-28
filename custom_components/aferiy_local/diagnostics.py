from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> dict[str, Any]:
    coordinator = hass.data[
        DOMAIN
    ][entry.entry_id]

    raw_packet = None

    if coordinator.last_raw_packet is not None:
        raw_packet = (
            coordinator.last_raw_packet.hex(" ")
        )

    registers_decimal = {
        f"R{register:02d}": value
        for register, value
        in coordinator.last_registers.items()
    }

    registers_hex = {
        f"R{register:02d}": f"0x{value:04X}"
        for register, value
        in coordinator.last_registers.items()
    }

    parsed_values = dict(
        coordinator.data or {}
    )

    profile = parsed_values.get(
        "device_profile",
        coordinator.last_profile_candidate,
    )

    diagnostics: dict[str, Any] = {
        "integration": (
            "AFERIY Local for Home Assistant"
        ),
        "mode": "read only",
        "bluetooth_name": (
            coordinator.last_device_name
        ),
        "device_profile": profile,
        "profile_candidate": (
            coordinator.last_profile_candidate
        ),
        "packet_length": (
            coordinator.last_packet_length
        ),
        "raw_packet_hex": raw_packet,
        "registers_decimal": (
            registers_decimal
        ),
        "registers_hex": registers_hex,
        "parsed_values": parsed_values,
    }

    if profile == "p180_pro":
        diagnostics[
            "p180_pro_debug"
        ] = {
            "battery_percent": (
                parsed_values.get(
                    "battery_percent"
                )
            ),
            "total_input_power": (
                parsed_values.get(
                    "total_input_power"
                )
            ),
            "total_output_power": (
                parsed_values.get(
                    "total_output_power"
                )
            ),
            "output_power": (
                parsed_values.get(
                    "output_power"
                )
            ),
            "ac_output_voltage": (
                parsed_values.get(
                    "ac_output_voltage"
                )
            ),
            "ac_output_frequency": (
                parsed_values.get(
                    "ac_output_frequency"
                )
            ),
            "battery_discharge_power": (
                parsed_values.get(
                    "battery_discharge_power"
                )
            ),
            "ac_active": (
                parsed_values.get(
                    "ac_active"
                )
            ),
            "dc_active": (
                parsed_values.get(
                    "dc_active"
                )
            ),
            "power_channel_1_r03": (
                parsed_values.get(
                    "power_channel_1"
                )
            ),
            "power_channel_2_r12": (
                parsed_values.get(
                    "power_channel_2"
                )
            ),
            "power_channel_3_r13": (
                parsed_values.get(
                    "power_channel_3"
                )
            ),
            "state_register_r75": (
                parsed_values.get(
                    "p180_state_register"
                )
            ),
            "dc_state_register_r78": (
                parsed_values.get(
                    "p180_dc_state_register"
                )
            ),
        }

    return diagnostics
