from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.components import bluetooth
from homeassistant.data_entry_flow import FlowResult

from .const import (
    CONF_ADDRESS,
    CONF_NAME,
    DEFAULT_NAME,
    DOMAIN,
)


class AferiyP280ConfigFlow(
    config_entries.ConfigFlow,
    domain=DOMAIN,
):
    VERSION = 1

    def __init__(self) -> None:
        self._discovered_address: str | None = None

    async def async_step_bluetooth(
        self,
        discovery_info: bluetooth.BluetoothServiceInfoBleak,
    ) -> FlowResult:
        """Handle automatic Bluetooth discovery."""

        bluetooth_name = discovery_info.name or ""
        address = discovery_info.address

        if not bluetooth_name.startswith("POWER"):
            return self.async_abort(
                reason="not_supported"
            )

        await self.async_set_unique_id(address)
        self._abort_if_unique_id_configured()

        self._discovered_address = address

        self.context["title_placeholders"] = {
            "name": DEFAULT_NAME
        }

        return await self.async_step_confirm()

    async def async_step_confirm(
        self,
        user_input: dict | None = None,
    ) -> FlowResult:
        """Confirm automatically discovered P280."""

        if user_input is not None:
            return self.async_create_entry(
                title=DEFAULT_NAME,
                data={
                    CONF_ADDRESS: self._discovered_address,
                    CONF_NAME: DEFAULT_NAME,
                },
            )

        return self.async_show_form(
            step_id="confirm"
        )

    async def async_step_user(
        self,
        user_input: dict | None = None,
    ) -> FlowResult:
        """Allow manual setup by choosing a discovered POWER device."""

        if user_input is not None:
            address = user_input[CONF_ADDRESS]

            await self.async_set_unique_id(address)
            self._abort_if_unique_id_configured()

            return self.async_create_entry(
                title=DEFAULT_NAME,
                data={
                    CONF_ADDRESS: address,
                    CONF_NAME: DEFAULT_NAME,
                },
            )

        await bluetooth.async_request_active_scan(
            self.hass
        )

        service_infos = bluetooth.async_discovered_service_info(
            self.hass,
            connectable=True,
        )

        discovered_devices: dict[str, str] = {}

        for service_info in service_infos:
            bluetooth_name = service_info.name or ""

            if bluetooth_name.startswith("POWER"):
                discovered_devices[
                    service_info.address
                ] = f"{bluetooth_name} ({service_info.address})"

        if not discovered_devices:
            return self.async_abort(
                reason="no_devices_found"
            )

        schema = vol.Schema(
            {
                vol.Required(
                    CONF_ADDRESS
                ): vol.In(
                    discovered_devices
                )
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
        )