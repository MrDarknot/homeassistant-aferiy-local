from __future__ import annotations

import asyncio
import logging
from datetime import timedelta

from bleak.exc import BleakError
from bleak_retry_connector import (
    BleakClientWithServiceCache,
    establish_connection,
)

from homeassistant.components import bluetooth
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import (
    CONF_ADDRESS,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    NOTIFY_UUID,
    WRITE_UUID,
)

_LOGGER = logging.getLogger(__name__)

STATE_USB_BIT = 512
STATE_DC_BIT = 1024
STATE_AC_BIT = 2048
STATE_LIGHT_BIT = 4096


def _crc16_modbus(data: bytes) -> int:
    crc = 0xFFFF

    for value in data:
        crc ^= value

        for _ in range(8):
            if crc & 1:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1

    return crc


def _build_status_request() -> bytes:
    payload = bytes(
        [
            0x11,
            0x04,
            0x00,
            0x00,
            0x00,
            0x50,
        ]
    )

    crc = _crc16_modbus(payload)

    return payload + bytes(
        [
            (crc >> 8) & 0xFF,
            crc & 0xFF,
        ]
    )


def _get_register(
    data: bytes,
    register: int,
) -> int:
    offset = 6 + register * 2

    if offset + 1 >= len(data):
        return 0

    return (
        data[offset] << 8
    ) | data[offset + 1]


def _get_all_registers(
    data: bytes,
) -> dict[int, int]:
    registers: dict[int, int] = {}

    for register in range(80):
        offset = 6 + register * 2

        if offset + 1 >= len(data):
            break

        registers[register] = _get_register(
            data,
            register,
        )

    return registers


def _parse_status(data: bytes) -> dict:
    if len(data) < 168:
        raise ValueError(
            f"Status packet too short: {len(data)} bytes"
        )

    if data[0] != 0x11 or data[1] != 0x04:
        raise ValueError(
            "Unexpected status packet"
        )

    state_flags = _get_register(
        data,
        41,
    )

    return {
        "battery_percent": _get_register(
            data,
            56,
        ) / 10.0,

        "total_input_power": _get_register(
            data,
            6,
        ),

        "total_output_power": _get_register(
            data,
            20,
        ),

        "output_power": _get_register(
            data,
            39,
        ),

        "system_power": _get_register(
            data,
            21,
        ),

        "remaining_minutes": _get_register(
            data,
            59,
        ),

        "time_to_full": _get_register(
            data,
            58,
        ),

        "usb_active": bool(
            state_flags & STATE_USB_BIT
        ),

        "dc_active": bool(
            state_flags & STATE_DC_BIT
        ),

        "ac_active": bool(
            state_flags & STATE_AC_BIT
        ),

        "light_active": bool(
            state_flags & STATE_LIGHT_BIT
        ),

        "connected": True,
    }


class AferiyLocalCoordinator(
    DataUpdateCoordinator
):
    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(
                seconds=DEFAULT_SCAN_INTERVAL
            ),
        )

        self.address = entry.data[
            CONF_ADDRESS
        ]

        self.last_raw_packet: bytes | None = None
        self.last_registers: dict[int, int] = {}
        self.last_device_name: str | None = None
        self.last_packet_length: int = 0

    async def _find_device(self):
        device = bluetooth.async_ble_device_from_address(
            self.hass,
            self.address,
            connectable=True,
        )

        if device is not None:
            return device

        await bluetooth.async_request_active_scan(
            self.hass
        )

        for _ in range(15):
            await asyncio.sleep(1)

            device = bluetooth.async_ble_device_from_address(
                self.hass,
                self.address,
                connectable=True,
            )

            if device is not None:
                return device

        raise UpdateFailed(
            f"AFERIY power station not reachable: {self.address}"
        )

    async def _async_update_data(
        self,
    ) -> dict:
        ble_device = await self._find_device()

        self.last_device_name = (
            ble_device.name or "Unknown"
        )

        response_event = asyncio.Event()
        received_data: bytes | None = None

        def notification_handler(
            _sender,
            data: bytearray,
        ) -> None:
            nonlocal received_data

            raw = bytes(data)

            if (
                len(raw) >= 2
                and raw[0] == 0x11
                and raw[1] == 0x04
            ):
                received_data = raw
                response_event.set()

        client = None

        try:
            client = await establish_connection(
                BleakClientWithServiceCache,
                ble_device,
                ble_device.name or "AFERIY Power Station",
                max_attempts=3,
            )

            await client.start_notify(
                NOTIFY_UUID,
                notification_handler,
            )

            await asyncio.sleep(0.5)

            request = _build_status_request()

            await client.write_gatt_char(
                WRITE_UUID,
                request,
                response=False,
            )

            await asyncio.wait_for(
                response_event.wait(),
                timeout=10,
            )

            if received_data is None:
                raise UpdateFailed(
                    "No status packet received"
                )

            self.last_raw_packet = received_data
            self.last_packet_length = len(
                received_data
            )
            self.last_registers = (
                _get_all_registers(
                    received_data
                )
            )

            _LOGGER.debug(
                "Raw AFERIY packet from %s: %s",
                self.last_device_name,
                received_data.hex(" "),
            )

            _LOGGER.debug(
                "AFERIY register dump from %s: %s",
                self.last_device_name,
                ", ".join(
                    f"R{register:02d}={value} "
                    f"(0x{value:04X})"
                    for register, value
                    in self.last_registers.items()
                ),
            )

            return _parse_status(
                received_data
            )

        except asyncio.TimeoutError as err:
            raise UpdateFailed(
                "Timed out waiting for AFERIY status"
            ) from err

        except BleakError as err:
            raise UpdateFailed(
                f"Bluetooth error: "
                f"{type(err).__name__}: {err}"
            ) from err

        except ValueError as err:
            raise UpdateFailed(
                f"Invalid AFERIY data: {err}"
            ) from err

        except Exception as err:
            raise UpdateFailed(
                f"Unexpected error: "
                f"{type(err).__name__}: {err}"
            ) from err

        finally:
            if client is not None:
                try:
                    if client.is_connected:
                        await client.stop_notify(
                            NOTIFY_UUID
                        )
                        await client.disconnect()

                except Exception:
                    pass
