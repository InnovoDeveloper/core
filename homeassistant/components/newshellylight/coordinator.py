"""Coordinator for ShellyLighting."""

import asyncio
from collections.abc import Callable
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import CONNECTION_TIMEOUT, PORT, SCAN_INTERVAL
from .controller import ShellyLight, ShellyLightController

_LOGGER = logging.getLogger(__name__)

type ShellyLightConfigEntry = ConfigEntry[ShellyCoordinator]


# My coordinator
class ShellyCoordinator(DataUpdateCoordinator[list[ShellyLight]]):
    """Shelly Lighting coordinator."""

    config_entry: ShellyLightConfigEntry

    def __init__(
        self, hass: HomeAssistant, config_entry: ShellyLightConfigEntry
    ) -> None:
        """Initialize my coordinator."""
        super().__init__(
            hass=hass,
            logger=_LOGGER,
            config_entry=config_entry,
            name="Shelly Lighting",
            update_interval=SCAN_INTERVAL,
        )
        self._controller = ShellyLightController(
            loop=hass.loop,
            port=PORT,
            ip_address=config_entry.data["IP Address"],
            discovery_enabled=True,
            discovery_interval=CONNECTION_TIMEOUT,
            discovered_callback=None,
            update_enabled=False,
        )

    async def start(self) -> None:
        """Start the Lea coordinator."""
        _LOGGER.debug("Starting Shelly coordinator")
        await self._controller.start()
        self._controller.send_update_message()

    async def set_discovery_callback(
        self, callback: Callable[[ShellyLight, bool], bool]
    ) -> None:
        """Set discovery callback for automatic Shelly discovery."""
        self._controller.set_light_discovered_callback(callback)

    def cleanup(self) -> asyncio.Event:
        """Stop and cleanup the cooridinator."""
        return self._controller.cleanup()

    async def turn_on(self, light: ShellyLight) -> None:
        """Turn on the zone."""
        await light.set_light_on(True)

    async def turn_off(self, light: ShellyLight) -> None:
        """Turn off the zone."""
        await light.set_light_off(False)

    @property
    def lights(self) -> list[ShellyLight]:
        """Return a list of discovered lights."""
        return self._controller.lights

    async def _async_update_data(self) -> list[ShellyLight]:
        _LOGGER.log(logging.INFO, "_async_update_data")
        self._controller.send_update_message()
        return self._controller.lights
