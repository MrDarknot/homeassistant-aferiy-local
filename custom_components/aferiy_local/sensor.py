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
    UnitOfElectricPotential,
    UnitOfFrequency,
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


P280_SENSORS = (
    AferiySensorDescription(
        key="battery",
        data_key="battery_percent",
        name="Battery",
        native_unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.BATTERY,
        state_class=SensorStateClass.MEASUREMENT,
    ),

    AferiySensorDescription(
        key="battery_charge_power",
        data_key="battery_charge_power",
        name="Battery charge power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
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
        key="ac_input_voltage",
        data_key="ac_input_voltage",
        name="AC input voltage",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),

    AferiySensorDescription(
        key="ac_input_frequency",
        data_key="ac_input_frequency",
        name="AC input frequency",
        native_unit_of_measurement=UnitOfFrequency.HERTZ,
        device_class=SensorDeviceClass.FREQUENCY,
        state_class=SensorStateClass.MEASUREMENT,
    ),

    AferiySensorDescription(
        key="ac_output_voltage",
        data_key="ac_output_voltage",
        name="AC output voltage",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),

    AferiySensorDescription(
        key="ac_frequency_setting",
        data_key="ac_frequency_setting",
        name="AC frequency",
        native_unit_of_measurement=UnitOfFrequency.HERTZ,
        device_class=SensorDeviceClass.FREQUENCY,
        state_class=SensorStateClass.MEASUREMENT,
    ),

    AferiySensorDescription(
        key="ac_output_power",
        data_key="ac_output_power",
        name="AC output power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),

    AferiySensorDescription(
        key="dc_output_power",
        data_key="dc_output_power",
        name="DC output power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),

    AferiySensorDescription(
        key="usb_c_pd140_right_power",
        data_key="usb_c_pd140_right_power",
        name="USB-C PD140 right power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),

    AferiySensorDescription(
        key="usb_c_pd140_left_power",
        data_key="usb_c_pd140_left_power",
        name="USB-C PD140 left power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),

    AferiySensorDescription(
        key="usb_c_pd20_left_power",
        data_key="usb_c_pd20_left_power",
        name="USB-C PD20 left power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),

    AferiySensorDescription(
        key="usb_c_pd20_right_power",
        data_key="usb_c_pd20_right_power",
        name="USB-C PD20 right power",
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


P180_PRO_SENSORS = (
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
        key="ac_output_voltage",
        data_key="ac_output_voltage",
        name="AC output voltage",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),

    AferiySensorDescription(
        key="ac_output_frequency",
        data_key="ac_output_frequency",
        name="AC output frequency",
        native_unit_of_measurement=UnitOfFrequency.HERTZ,
        device_class=SensorDeviceClass.FREQUENCY,
        state_class=SensorStateClass.MEASUREMENT,
    ),

    AferiySensorDescription(
        key="battery_discharge_power",
        data_key="battery_discharge_power",
        name="Battery discharge power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
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
        sensors = P180_PRO_SENSORS
    else:
        sensors = P280_SENSORS

    async_add_entities(
        AferiyPowerStationSensor(
            coordinator,
            entry,
            description,
            profile,
        )
        for description in sensors
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
            model = "P280"

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
    def native_value(self):
        return self.coordinator.data.get(
            self.entity_description.data_key
        )
