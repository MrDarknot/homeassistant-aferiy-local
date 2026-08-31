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

STATE_USB_BIT = 0x0200
STATE_DC_BIT = 0x0400
STATE_AC_BIT = 0x0800
STATE_LIGHT_BIT = 0x1000


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


def _looks_like_p180_pro(
    registers: dict[int, int],
) -> bool:
    battery = registers.get(31, 0)

    return (
        0 <= battery <= 100
        and registers.get(36) == 0x3000
        and registers.get(38) == 0x3000
        and registers.get(63) == 0x352C
        and registers.get(60) == registers.get(61)
        and registers.get(66) == registers.get(67)
    )


def _parse_p280_status(
    data: bytes,
) -> dict:
    state_flags = _get_register(
        data,
        41,
    )

    return {
        "battery_percent": (
            _get_register(data, 56) / 10.0
        ),

        "battery_charge_power": (
            _get_register(data, 3)
        ),

        "total_input_power": (
            _get_register(data, 6)
        ),

        "dc_output_power": (
            _get_register(data, 10) / 10.0
        ),

        "ac_output_voltage": (
            _get_register(data, 18) / 10.0
        ),

        "ac_frequency_setting": (
            _get_register(data, 19) / 10.0
        ),

        "ac_output_power": (
            _get_register(data, 20)
        ),

        "ac_input_voltage": (
            _get_register(data, 21) / 10.0
        ),

        "ac_input_frequency": (
            _get_register(data, 22) / 100.0
        ),

        "usb_c_pd140_right_power": (
            _get_register(data, 34) / 10.0
        ),

        "usb_c_pd140_left_power": (
            _get_register(data, 35) / 10.0
        ),

        "usb_c_pd20_left_power": (
            _get_register(data, 36) / 10.0
        ),

        "usb_c_pd20_right_power": (
            _get_register(data, 37) / 10.0
        ),

        "total_output_power": (
            _get_register(data, 39)
        ),

        "remaining_minutes": (
            _get_register(data, 59)
        ),

        "time_to_full": (
            _get_register(data, 58)
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

        "device_profile": "p280",
    }


def _parse_p180_pro_status(
    data: bytes,
) -> dict:
    registers = _get_all_registers(
        data
    )

    battery_percent = registers.get(
        31,
        0,
    )

    ac_input_power = registers.get(
        2,
        0,
    )

    power_channel_1 = registers.get(
        3,
        0,
    )

    power_channel_2 = registers.get(
        12,
        0,
    )

    power_channel_3 = registers.get(
        13,
        0,
    )

    raw_ac_input_voltage = (
        registers.get(8, 0) / 10.0
    )

    ac_input_frequency = (
        registers.get(9, 0) / 100.0
    )

    ac_output_voltage = (
        registers.get(10, 0) / 10.0
    )

    ac_frequency_setting = (
        registers.get(11, 0) / 10.0
    )

    battery_voltage_candidate = (
        registers.get(32, 0) / 100.0
    )

    state_register = registers.get(
        75,
        0,
    )

    dc_state_register = registers.get(
        78,
        0,
    )

    source_register = registers.get(
        53,
        0,
    )

    ac_active = bool(
        state_register & 0x10
    )

    dc_active = bool(
        dc_state_register
    )

    #
    # AC INPUT
    #
    # R02 = AC input power.
    #
    # R08 occasionally reports a few volts of noise
    # when no AC source is connected.
    #
    # If both AC power and AC frequency are zero,
    # report AC input voltage as zero as well.
    #

    if (
        ac_input_power == 0
        and ac_input_frequency == 0
    ):
        ac_input_voltage = 0.0
    else:
        ac_input_voltage = (
            raw_ac_input_voltage
        )

    #
    # SOLAR / DC INPUT
    #
    # Controlled tests:
    #
    # Solar charging:
    # R03 = displayed solar input
    # R53 = 0x0300
    #
    # Solar input while AC output is active:
    # R03 = displayed solar input
    # R53 = 0x0310
    #
    # AC charging:
    # R53 = 0x0068
    #
    # The upper source bits in R53 are therefore used
    # as an additional guard before exposing R03 as
    # Solar / DC input power.
    #

    solar_dc_source_active = (
        source_register & 0x0300
    ) == 0x0300

    if solar_dc_source_active:
        solar_dc_input_power = (
            power_channel_1
        )
    else:
        solar_dc_input_power = 0

    #
    # TOTAL INPUT
    #
    # AC and Solar / DC have been validated separately.
    # Simultaneous AC + Solar charging has not yet been
    # validated, so preserve source priority for now.
    #

    if ac_input_power > 0:
        total_input_power = (
            ac_input_power
        )
    else:
        total_input_power = (
            solar_dc_input_power
        )

    #
    # TIME
    #
    # R71 = Time to Full
    #
    # Confirmed against the P180 Pro display at several
    # different charge rates and SOC levels.
    #
    # R72 = Remaining Time
    #
    # Confirmed during net battery discharge:
    # R72 = 179 minutes while the display showed
    # approximately 3 hours remaining.
    #

    time_to_full = registers.get(
        71,
        0,
    )

    remaining_minutes = registers.get(
        72,
        0,
    )

    #
    # OUTPUT
    #
    # P180 Pro output mapping remains experimental.
    # Keep the previously tested behaviour until more
    # controlled output tests are available.
    #

    output_power = 0

    if ac_active:
        if power_channel_2 > 0:
            output_power = (
                power_channel_2
            )

        elif power_channel_3 > 0:
            output_power = (
                power_channel_3
            )

        elif power_channel_1 > 0:
            output_power = (
                power_channel_1
            )

    return {
        "battery_percent": float(
            battery_percent
        ),

        "ac_input_power": (
            ac_input_power
        ),

        "solar_dc_input_power": (
            solar_dc_input_power
        ),

        "total_input_power": (
            total_input_power
        ),

        "ac_input_voltage": (
            ac_input_voltage
        ),

        "ac_input_frequency": (
            ac_input_frequency
        ),

        "ac_output_voltage": (
            ac_output_voltage
        ),

        "ac_output_frequency": (
            ac_frequency_setting
        ),

        "ac_frequency_setting": (
            ac_frequency_setting
        ),

        "total_output_power": (
            output_power
        ),

        "output_power": (
            output_power
        ),

        "battery_discharge_power": (
            power_channel_3
        ),

        "remaining_minutes": (
            remaining_minutes
        ),

        "time_to_full": (
            time_to_full
        ),

        "usb_active": False,

        "dc_active": (
            dc_active
        ),

        "ac_active": (
            ac_active
        ),

        "light_active": False,

        "connected": True,

        "device_profile": (
            "p180_pro"
        ),

        #
        # DEBUG / RESEARCH VALUES
        #

        "battery_voltage_candidate": (
            battery_voltage_candidate
        ),

        "power_channel_1": (
            power_channel_1
        ),

        "power_channel_2": (
            power_channel_2
        ),

        "power_channel_3": (
            power_channel_3
        ),

        "p180_state_register": (
            state_register
        ),

        "p180_dc_state_register": (
            dc_state_register
        ),

        "p180_source_register": (
            source_register
        ),
    }


def _parse_status(
    data: bytes,
    profile: str,
) -> dict:
    if len(data) < 168:
        raise ValueError(
            f"Status packet too short: {len(data)} bytes"
        )

    if (
        data[0] != 0x11
        or data[1] != 0x04
    ):
        raise ValueError(
            "Unexpected status packet"
        )

    if profile == "p180_pro":
        return _parse_p180_pro_status(
            data
        )

    return _parse_p280_status(
        data
    )


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
        self.last_profile_candidate: str = "unknown"

        self._p180_profile_locked = False


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

            self.last_raw_packet = (
                received_data
            )

            self.last_packet_length = len(
                received_data
            )

            self.last_registers = (
                _get_all_registers(
                    received_data
                )
            )

            if _looks_like_p180_pro(
                self.last_registers
            ):
                self.last_profile_candidate = (
                    "p180_pro"
                )

                self._p180_profile_locked = True

            else:
                self.last_profile_candidate = (
                    "standard"
                )

            if self._p180_profile_locked:
                active_profile = (
                    "p180_pro"
                )
            else:
                active_profile = (
                    "p280"
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

            _LOGGER.debug(
                "AFERIY detected profile candidate for %s: %s",
                self.last_device_name,
                self.last_profile_candidate,
            )

            _LOGGER.debug(
                "AFERIY active profile for %s: %s",
                self.last_device_name,
                active_profile,
            )

            parsed = _parse_status(
                received_data,
                active_profile,
            )

            if active_profile == "p180_pro":
                _LOGGER.debug(
                    "P180 Pro parsed values: "
                    "battery=%s%%, "
                    "AC input=%sW, "
                    "solar/DC input=%sW, "
                    "total input=%sW, "
                    "time to full=%smin, "
                    "remaining=%smin, "
                    "output=%sW, "
                    "AC=%s, "
                    "DC=%s",
                    parsed.get(
                        "battery_percent"
                    ),
                    parsed.get(
                        "ac_input_power"
                    ),
                    parsed.get(
                        "solar_dc_input_power"
                    ),
                    parsed.get(
                        "total_input_power"
                    ),
                    parsed.get(
                        "time_to_full"
                    ),
                    parsed.get(
                        "remaining_minutes"
                    ),
                    parsed.get(
                        "output_power"
                    ),
                    parsed.get(
                        "ac_active"
                    ),
                    parsed.get(
                        "dc_active"
                    ),
                )

            return parsed

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
