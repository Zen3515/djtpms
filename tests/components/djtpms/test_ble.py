"""Tests for the DJTPMS BLE parser."""

from __future__ import annotations

from bleak.backends.device import BLEDevice
from bluetooth_data_tools import monotonic_time_coarse
import pytest

from homeassistant.components.bluetooth import BluetoothServiceInfoBleak
from homeassistant.components.djtpms.ble import parse_djtpms_service_info


def _make_bluetooth_service_info(
    manufacturer_data: dict[int, bytes],
    address: str,
) -> BluetoothServiceInfoBleak:
    """Create a BluetoothServiceInfoBleak object for testing."""
    return BluetoothServiceInfoBleak(
        name="DJTPMS",
        manufacturer_data=manufacturer_data,
        service_uuids=["0000ffe0-0000-1000-8000-00805f9b34fb"],
        address=address,
        rssi=-74,
        service_data={},
        source="local",
        device=BLEDevice(
            name="DJTPMS",
            address=address,
            details={},
        ),
        time=monotonic_time_coarse(),
        advertisement=None,
        connectable=True,
        tx_power=0,
        raw=None,
    )


@pytest.mark.parametrize(
    ("payload_hex", "expected_battery", "expected_temp", "expected_abs", "expected_gauge"),
    [
        ("1F1D014400CB0C3D5E4E8BE6", 3.1, 29, 0x0144, 223),
        ("1E1E012A004C0C3D5E4E8B8A", 3.0, 30, 0x012A, 197),
    ],
)
def test_parse_djtpms_payloads(
    payload_hex: str,
    expected_battery: float,
    expected_temp: int,
    expected_abs: int,
    expected_gauge: int,
) -> None:
    """Validate parsed values from captured DJTPMS payloads."""
    service_info = _make_bluetooth_service_info(
        manufacturer_data={0: bytes.fromhex(payload_hex)},
        address="0C:3D:5E:4E:8B:8A",
    )
    parsed = parse_djtpms_service_info(service_info)
    assert parsed is not None
    assert parsed.battery_voltage == pytest.approx(expected_battery)
    assert parsed.temperature == expected_temp
    assert parsed.absolute_pressure == expected_abs
    assert parsed.gauge_pressure == expected_gauge
