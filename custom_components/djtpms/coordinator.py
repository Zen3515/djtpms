"""Coordinator for DJTPMS Bluetooth devices."""

from __future__ import annotations

import logging

from homeassistant.components.bluetooth import BluetoothScanningMode
from homeassistant.components.bluetooth.passive_update_processor import (
    PassiveBluetoothProcessorCoordinator,
)
from homeassistant.core import HomeAssistant

from .ble import DjtpmsAdvertisement, parse_djtpms_service_info

_LOGGER = logging.getLogger(__name__)


type DjtpmsBluetoothUpdate = DjtpmsAdvertisement | None


class DjtpmsCoordinator(
    PassiveBluetoothProcessorCoordinator[DjtpmsBluetoothUpdate]
):
    """Process DJTPMS advertisements from a single address."""

    def __init__(self, hass: HomeAssistant, address: str) -> None:
        """Initialize the DJTPMS coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            address=address,
            mode=BluetoothScanningMode.PASSIVE,
            update_method=parse_djtpms_service_info,
            connectable=False,
        )
