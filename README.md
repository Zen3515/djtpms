![DJTPMS](img/icon@2x.jpeg)

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg?style=for-the-badge)](https://github.com/hacs/integration)
[![License](https://img.shields.io/github/license/Zen3515/djtpms.svg?style=for-the-badge&color=yellow)](LICENSE)
![GitHub all releases](https://img.shields.io/github/downloads/Zen3515/djtpms/total?style=for-the-badge&logo=appveyor)

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

You can add DJTPMS from the Home Assistant UI.

[![Open your Home Assistant instance and start setting up a new integration.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=djtpms)

Notes:
- Bluetooth must be enabled in Home Assistant.
- The device must be in range and actively advertising.

## Entities

The integration creates the following sensor entities per device:
- Battery voltage (V)
- Temperature (°C)
- Absolute pressure (kPa)
- Gauge pressure (kPa)

Gauge pressure is derived by subtracting a fixed 101 kPa atmospheric pressure from the absolute pressure.

## Bluetooth Payload Format

The DJTPMS advertisement frame is parsed from manufacturer or service data. The core 12-byte payload layout is:

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

Derived values follow the parsing logic in `custom_components/djtpms/ble.py` and constants in `custom_components/djtpms/const.py`:
- Battery voltage (V) = `VV / 10.0`
- Temperature (°C) = signed int8 conversion of `TT` (0..255 -> -128..127)
- Absolute pressure (kPa) = `(PH << 8) | PL` (big-endian uint16)
- Gauge pressure (kPa) = `max(absolute_pressure - 101, 0)`

CRC8 is computed over `[CID0, CID1, VV, TT, PH, PL]` and compared to `CC`.

## Support

If you have discovered a problem or want to request a feature, please open an issue.

Pull requests are welcome.
