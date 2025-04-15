"""The Shelly_Lighting integration."""

from __future__ import annotations

import asyncio
from contextlib import suppress
from errno import EADDRINUSE
import logging

from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .const import CONNECTION_TIMEOUT, DOMAIN, PORT
from .coordinator import ShellyCoordinator, ShellyLightConfigEntry

PLATFORMS: list[Platform] = [Platform.LIGHT]
_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ShellyLightConfigEntry) -> bool:
    """Set up Shelly_Lighting from a config entry."""

    ip_address = entry.data["IP Address"]
    hass.data[DOMAIN] = {"ip": ip_address}

    _LOGGER.log(logging.INFO, "async_setup_entry")
    _LOGGER.log(logging.INFO, "ip_address: %s", str(ip_address))

    coordinator = ShellyCoordinator(hass, entry)

    async def await_cleanup():
        """Disable discovery, disable update, Close connections."""
        _LOGGER.log(logging.INFO, "await_cleanup")

        cleanup_complete: asyncio.Event = coordinator.cleanup()
        with suppress(TimeoutError):
            await asyncio.wait_for(cleanup_complete.wait(), 1)

    entry.async_on_unload(await_cleanup)
    try:
        await coordinator.start()
    except OSError as ex:
        if ex.errno != EADDRINUSE:
            _LOGGER.error("Start failed, errno: %d", ex.errno)
            return False
        _LOGGER.error("Port %s already in use", PORT)
        raise ConfigEntryNotReady from ex

    await coordinator.async_config_entry_first_refresh()

    try:
        async with asyncio.timeout(delay=CONNECTION_TIMEOUT):
            while not coordinator.lights:
                await asyncio.sleep(delay=1)
    except TimeoutError as ex:
        raise ConfigEntryNotReady from ex

    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(
    hass: HomeAssistant, entry: ShellyLightConfigEntry
) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
