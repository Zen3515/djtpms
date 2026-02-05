# DJTPMS

DJTPMS is a Home Assistant integration that listens to Bluetooth LE advertisements from DJTPMS sensors and exposes their readings as sensors.

DJTPMS sensors are commonly sold as generic tire pressure sensors on AliExpress.

This integration uses passive Bluetooth scanning only and does not connect to the device.

## Installation

HACS:
1. Add this repository to HACS as a custom repository (Integration).
2. Install `DJTPMS`.
3. Restart Home Assistant.

Manual:
1. Copy `custom_components/djtpms` to `/config/custom_components/djtpms`.
2. Restart Home Assistant.

## Configuration

Add the integration from the Home Assistant UI. Bluetooth must be enabled and the device must be in range and actively advertising.

## Entities

- Battery voltage (V)
- Temperature (°C)
- Absolute pressure (kPa)
- Gauge pressure (kPa)

Gauge pressure is derived by subtracting a fixed 101 kPa atmospheric pressure from the absolute pressure.

## Bluetooth Payload Format

```text
00 00  1F 27  01 54  00  06  0C 3D 5E 4E 8B E6
|  |    |  |   |  |   |   |   \______________/
|  |    |  |   |  |   |   \---- CC = CRC8 check byte
|  |    |  |   |  |   \-------- FF = flags/unknown (often 00)
|  |    |  |   \--\----------- PH PL = abs pressure (kPa), big-endian uint16
|  |    \--\------------------ TT = temperature (°C)
|  \-------------------------- VV = battery*10  (e.g. 0x1F => 3.1V)
\----------------------------- CID0 CID1 = “Company ID” bytes (varies: 00 00 or 00 0C)
```

## Calculations

See `custom_components/djtpms/ble.py` and `custom_components/djtpms/const.py` for the exact parsing logic.
- Battery voltage (V) = `VV / 10.0`
- Temperature (°C) = signed int8 conversion of `TT` (0..255 -> -128..127)
- Absolute pressure (kPa) = `(PH << 8) | PL` (big-endian uint16)
- Gauge pressure (kPa) = `max(absolute_pressure - 101, 0)`

CRC8 is computed over `[CID0, CID1, VV, TT, PH, PL]` and compared to `CC`.
