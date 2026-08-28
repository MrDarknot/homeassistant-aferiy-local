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
        raw_packet = coordinator.last_raw_packet.hex(" ")

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

    return {
        "integration": "AFERIY Local for Home Assistant",
        "mode": "read only",
        "bluetooth_name": coordinator.last_device_name,
        "packet_length": coordinator.last_packet_length,
        "raw_packet_hex": raw_packet,
        "registers_decimal": registers_decimal,
        "registers_hex": registers_hex,
        "parsed_values": dict(
            coordinator.data or {}
        ),
    }
