"""Tests for the DJTPMS sensor platform."""

from __future__ import annotations

import pytest

from homeassistant.components.djtpms.ble import DjtpmsAdvertisement
from homeassistant.components.djtpms.const import (
    SENSOR_BATTERY_PERCENTAGE,
    SENSOR_BATTERY_VOLTAGE,
)
from homeassistant.components.djtpms.sensor import (
    _battery_percentage_from_voltage,
    _entity_key,
    _sensor_update_to_bluetooth_data_update,
)


@pytest.mark.parametrize(
    ("voltage", "expected_percentage"),
    [
        (3.4, 100),
        (3.3, 100),
        (3.05, 97),
        (2.92, 83),
        (2.875, 50),
        (2.72, 10),
        (2.6, 0),
        (2.59, 0),
    ],
)
def test_battery_percentage_from_voltage(
    voltage: float, expected_percentage: int
) -> None:
    """Battery percentage should follow the configured discharge curve."""
    assert _battery_percentage_from_voltage(voltage) == expected_percentage


def test_sensor_update_includes_battery_percentage() -> None:
    """A valid update should include derived battery percentage data."""
    update = DjtpmsAdvertisement(
        battery_voltage=2.875,
        temperature=30,
        absolute_pressure=320,
        gauge_pressure=219,
    )

    data_update = _sensor_update_to_bluetooth_data_update(update)

    assert data_update.entity_data[_entity_key(SENSOR_BATTERY_PERCENTAGE)] == 50
    assert data_update.entity_data[_entity_key(SENSOR_BATTERY_VOLTAGE)] == pytest.approx(
        2.875
    )
