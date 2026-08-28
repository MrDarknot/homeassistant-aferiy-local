from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import (
    AddEntitiesCallback,
)
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
)

from .const import (
    CONF_ADDRESS,
    CONF_NAME,
    DOMAIN,
)
from .coordinator import AferiyLocalCoordinator


@dataclass(
    frozen=True,
    kw_only=True,
)
class AferiyBinarySensorDescription(
    BinarySensorEntityDescription
):
    data_key: str


P280_BINARY_SENSORS = (
    AferiyBinarySensorDescription(
        key="ac_output",
        data_key="ac_active",
        name="AC output",
    ),
    AferiyBinarySensorDescription(
        key="dc_output",
        data_key="dc_active",
        name="DC output",
    ),
    AferiyBinarySensorDescription(
        key="usb_output",
        data_key="usb_active",
        name="USB output",
    ),
    AferiyBinarySensorDescription(
        key="light",
        data_key="light_active",
        name="Light",
    ),
    AferiyBinarySensorDescription(
        key="bluetooth_connected",
        data_key="connected",
        name="Bluetooth connected",
    ),
)


P180_PRO_BINARY_SENSORS = (
    AferiyBinarySensorDescription(
        key="ac_output",
        data_key="ac_active",
        name="AC output",
    ),
    AferiyBinarySensorDescription(
        key="dc_output",
        data_key="dc_active",
        name="DC output",
    ),
    AferiyBinarySensorDescription(
        key="bluetooth_connected",
        data_key="connected",
        name="Bluetooth connected",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: AferiyLocalCoordinator = hass.data[
        DOMAIN
    ][entry.entry_id]

    profile = coordinator.data.get(
        "device_profile",
        "p280",
    )

    if profile == "p180_pro":
        binary_sensors = (
            P180_PRO_BINARY_SENSORS
        )
    else:
        binary_sensors = (
            P280_BINARY_SENSORS
        )

    async_add_entities(
        AferiyPowerStationBinarySensor(
            coordinator,
            entry,
            description,
            profile,
        )
        for description in binary_sensors
    )


class AferiyPowerStationBinarySensor(
    CoordinatorEntity[AferiyLocalCoordinator],
    BinarySensorEntity,
):
    entity_description: AferiyBinarySensorDescription

    def __init__(
        self,
        coordinator: AferiyLocalCoordinator,
        entry: ConfigEntry,
        description: AferiyBinarySensorDescription,
        profile: str,
    ) -> None:
        super().__init__(
            coordinator
        )

        self.entity_description = description

        address = entry.data[
            CONF_ADDRESS
        ]

        name = entry.data[
            CONF_NAME
        ]

        self._attr_unique_id = (
            f"{address}_{description.key}"
        )

        if profile == "p180_pro":
            model = "P180 Pro"
        else:
            model = "Power Station"

        self._attr_device_info = DeviceInfo(
            identifiers={
                (
                    DOMAIN,
                    address,
                )
            },
            name=name,
            manufacturer="AFERIY",
            model=model,
        )

    @property
    def is_on(self) -> bool:
        return bool(
            self.coordinator.data.get(
                self.entity_description.data_key
            )
        )
