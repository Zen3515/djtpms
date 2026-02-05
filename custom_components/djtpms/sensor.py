"""Support for DJTPMS sensors."""

from __future__ import annotations

from homeassistant.components.bluetooth.passive_update_processor import (
    PassiveBluetoothDataProcessor,
    PassiveBluetoothDataUpdate,
    PassiveBluetoothEntityKey,
    PassiveBluetoothProcessorEntity,
)
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import (
    EntityCategory,
    UnitOfElectricPotential,
    UnitOfPressure,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityDescription
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import DjtpmsConfigEntry
from .coordinator import DjtpmsBluetoothUpdate
from .const import (
    SENSOR_BATTERY_VOLTAGE,
    SENSOR_PRESSURE_ABSOLUTE,
    SENSOR_PRESSURE_GAUGE,
    SENSOR_TEMPERATURE,
)

SENSOR_DESCRIPTIONS: dict[str, SensorEntityDescription] = {
    SENSOR_BATTERY_VOLTAGE: SensorEntityDescription(
        key=SENSOR_BATTERY_VOLTAGE,
        name="Battery voltage",
        device_class=SensorDeviceClass.VOLTAGE,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SENSOR_TEMPERATURE: SensorEntityDescription(
        key=SENSOR_TEMPERATURE,
        name="Temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SENSOR_PRESSURE_ABSOLUTE: SensorEntityDescription(
        key=SENSOR_PRESSURE_ABSOLUTE,
        name="Absolute pressure",
        device_class=SensorDeviceClass.PRESSURE,
        native_unit_of_measurement=UnitOfPressure.KPA,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SENSOR_PRESSURE_GAUGE: SensorEntityDescription(
        key=SENSOR_PRESSURE_GAUGE,
        name="Gauge pressure",
        device_class=SensorDeviceClass.PRESSURE,
        native_unit_of_measurement=UnitOfPressure.KPA,
        state_class=SensorStateClass.MEASUREMENT,
    ),
}

VALUE_ATTRS: dict[str, str] = {
    SENSOR_BATTERY_VOLTAGE: "battery_voltage",
    SENSOR_TEMPERATURE: "temperature",
    SENSOR_PRESSURE_ABSOLUTE: "absolute_pressure",
    SENSOR_PRESSURE_GAUGE: "gauge_pressure",
}


def _entity_key(key: str) -> PassiveBluetoothEntityKey:
    """Return an entity key for the DJTPMS device."""
    return PassiveBluetoothEntityKey(key, None)


def _value_for_key(update: DjtpmsBluetoothUpdate, key: str) -> float | int | None:
    """Return the value for a given sensor key."""
    if update is None:
        return None

    if (attr := VALUE_ATTRS.get(key)) is None:
        return None

    return getattr(update, attr)


def _sensor_update_to_bluetooth_data_update(
    update: DjtpmsBluetoothUpdate,
) -> PassiveBluetoothDataUpdate[float | int]:
    """Convert a DJTPMS update to a Bluetooth data update."""
    if update is None:
        return PassiveBluetoothDataUpdate()

    data: dict[PassiveBluetoothEntityKey, float | int] = {}
    names: dict[PassiveBluetoothEntityKey, str | None] = {}
    descriptions: dict[PassiveBluetoothEntityKey, EntityDescription] = {}

    for key, description in SENSOR_DESCRIPTIONS.items():
        if (value := _value_for_key(update, key)) is None:
            continue
        entity_key = _entity_key(key)
        data[entity_key] = value
        names[entity_key] = description.name
        descriptions[entity_key] = description

    return PassiveBluetoothDataUpdate(
        entity_descriptions=descriptions,
        entity_data=data,
        entity_names=names,
    )


async def async_setup_entry(
    hass: HomeAssistant,
    entry: DjtpmsConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up DJTPMS sensors based on a config entry."""
    processor = PassiveBluetoothDataProcessor(_sensor_update_to_bluetooth_data_update)
    entry.async_on_unload(
        processor.async_add_entities_listener(
            DjtpmsBluetoothSensorEntity, async_add_entities
        )
    )
    entry.async_on_unload(entry.runtime_data.async_register_processor(processor))


class DjtpmsBluetoothSensorEntity(
    PassiveBluetoothProcessorEntity[
        PassiveBluetoothDataProcessor[float | int, DjtpmsBluetoothUpdate]
    ],
    SensorEntity,
):
    """Representation of a DJTPMS sensor."""

    @property
    def native_value(self) -> float | int | None:
        """Return the native value."""
        return self.processor.entity_data.get(self.entity_key)
