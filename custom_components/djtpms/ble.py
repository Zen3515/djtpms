"""Bluetooth parsing for DJTPMS."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from homeassistant.components.bluetooth import BluetoothServiceInfoBleak

from .const import ATMOSPHERIC_PRESSURE_KPA, CRC8_INIT, CRC8_POLY, PAYLOAD_MIN_LENGTH


@dataclass(slots=True, frozen=True)
class DjtpmsAdvertisement:
    """Parsed DJTPMS advertisement data."""

    battery_voltage: float
    temperature: int
    absolute_pressure: int
    gauge_pressure: int


def parse_djtpms_service_info(
    service_info: BluetoothServiceInfoBleak,
) -> DjtpmsAdvertisement | None:
    """Parse DJTPMS data from a BluetoothServiceInfoBleak."""
    for payload, manufacturer_id in _iter_payloads(service_info):
        if (parsed := _parse_payload(payload, manufacturer_id)) is not None:
            return parsed
    return None


def _iter_payloads(
    service_info: BluetoothServiceInfoBleak,
) -> Iterable[tuple[bytes, int | None]]:
    """Yield candidate payloads from the advertisement."""
    for manufacturer_id, payload in service_info.manufacturer_data.items():
        yield payload, manufacturer_id
    for payload in service_info.service_data.values():
        yield payload, None


def _parse_payload(
    payload: bytes, manufacturer_id: int | None
) -> DjtpmsAdvertisement | None:
    """Parse a candidate payload into DJTPMS data."""
    if len(payload) < PAYLOAD_MIN_LENGTH:
        return None

    for cid0, cid1, payload12 in _extract_frames(payload, manufacturer_id):
        crc_input = bytes(
            [cid0, cid1, payload12[0], payload12[1], payload12[2], payload12[3]]
        )
        if _crc8(crc_input) != payload12[5]:
            continue

        battery_voltage = payload12[0] / 10.0
        temperature = _to_int8(payload12[1])
        absolute_pressure = (payload12[2] << 8) | payload12[3]
        gauge_pressure = max(absolute_pressure - ATMOSPHERIC_PRESSURE_KPA, 0)

        return DjtpmsAdvertisement(
            battery_voltage=battery_voltage,
            temperature=temperature,
            absolute_pressure=absolute_pressure,
            gauge_pressure=gauge_pressure,
        )

    return None


def _extract_frames(
    payload: bytes, manufacturer_id: int | None
) -> Iterable[tuple[int, int, bytes]]:
    """Extract the DJTPMS frames from a payload."""
    if manufacturer_id is not None:
        cid0 = manufacturer_id & 0xFF
        cid1 = (manufacturer_id >> 8) & 0xFF
        cid_pairs = [(cid0, cid1)]
        if cid0 != cid1:
            cid_pairs.append((cid1, cid0))
        if len(payload) >= 14:
            frame14 = payload[-14:]
            for cid_a, cid_b in cid_pairs:
                if frame14[0] == cid_a and frame14[1] == cid_b:
                    yield cid_a, cid_b, frame14[2:]
        if len(payload) >= 12:
            for cid_a, cid_b in cid_pairs:
                yield cid_a, cid_b, payload[-12:]
        return

    if len(payload) >= 14:
        frame14 = payload[-14:]
        yield frame14[0], frame14[1], frame14[2:]


def _to_int8(value: int) -> int:
    """Interpret 0..255 as signed int8 (-128..127)."""
    return value - 256 if value >= 128 else value


def _crc8(data: bytes) -> int:
    """Compute CRC8 over data."""
    crc = CRC8_INIT
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 0x80:
                crc = ((crc << 1) & 0xFF) ^ CRC8_POLY
            else:
                crc = (crc << 1) & 0xFF
    return crc
