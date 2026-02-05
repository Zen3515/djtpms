"""The DJTPMS integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .coordinator import DjtpmsCoordinator

PLATFORMS: list[Platform] = [Platform.SENSOR]

type DjtpmsConfigEntry = ConfigEntry[DjtpmsCoordinator]


async def async_setup_entry(hass: HomeAssistant, entry: DjtpmsConfigEntry) -> bool:
    """Set up DJTPMS from a config entry."""
    address = entry.unique_id
    assert address is not None

    entry.runtime_data = DjtpmsCoordinator(hass, address)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Only start after all platforms have had a chance to subscribe.
    entry.async_on_unload(entry.runtime_data.async_start())
    return True


async def async_unload_entry(hass: HomeAssistant, entry: DjtpmsConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
