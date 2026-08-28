from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE,
    UnitOfPower,
    UnitOfTime,
)
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
class AferiySensorDescription(
    SensorEntityDescription
):
    data_key: str


SENSORS = (
    AferiySensorDescription(
        key="battery",
        data_key="battery_percent",
        name="Battery",
        native_unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.BATTERY,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    AferiySensorDescription(
        key="total_input_power",
        data_key="total_input_power",
        name="Total input power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    AferiySensorDescription(
        key="total_output_power",
        data_key="total_output_power",
        name="Total output power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    AferiySensorDescription(
        key="output_power",
        data_key="output_power",
        name="Output power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    AferiySensorDescription(
        key="system_power",
        data_key="system_power",
        name="System power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    AferiySensorDescription(
        key="remaining_time",
        data_key="remaining_minutes",
        name="Remaining time",
        native_unit_of_measurement=UnitOfTime.MINUTES,
        device_class=SensorDeviceClass.DURATION,
    ),
    AferiySensorDescription(
        key="time_to_full",
        data_key="time_to_full",
        name="Time to full",
        native_unit_of_measurement=UnitOfTime.MINUTES,
        device_class=SensorDeviceClass.DURATION,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = hass.data[
        DOMAIN
    ][entry.entry_id]

    async_add_entities(
        AferiyPowerStationSensor(
            coordinator,
            entry,
            description,
        )
        for description in SENSORS
    )


class AferiyPowerStationSensor(
    CoordinatorEntity[AferiyLocalCoordinator],
    SensorEntity,
):
    entity_description: AferiySensorDescription

    def __init__(
        self,
        coordinator: AferiyLocalCoordinator,
        entry: ConfigEntry,
        description: AferiySensorDescription,
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

        self._attr_device_info = DeviceInfo(
            identifiers={
                (
                    DOMAIN,
                    address,
                )
            },
            name=name,
            manufacturer="AFERIY",
            model="Power Station",
        )

    @property
    def native_value(self):
        return self.coordinator.data.get(
            self.entity_description.data_key
        )
