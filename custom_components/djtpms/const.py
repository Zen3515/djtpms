"""Constants for the DJTPMS integration."""

from __future__ import annotations

from typing import Final

DOMAIN: Final = "djtpms"

ATMOSPHERIC_PRESSURE_KPA: Final = 101
PAYLOAD_MIN_LENGTH: Final = 12

# CRC8 parameters used by DJTPMS (MSB-first).
CRC8_POLY: Final = 0x2F
CRC8_INIT: Final = 0xDF

SENSOR_BATTERY_VOLTAGE: Final = "battery_voltage"
SENSOR_TEMPERATURE: Final = "temperature"
SENSOR_PRESSURE_ABSOLUTE: Final = "absolute_pressure"
SENSOR_PRESSURE_GAUGE: Final = "gauge_pressure"
