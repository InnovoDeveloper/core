"""Controller."""

from __future__ import annotations

import asyncio
from collections.abc import Callable
import logging
import socket
from typing import Any

from .const import DISCOVERY_INTERVAL, PORT, UPDATE_INTERVAL
from .light import ShellyLight

_LOGGER = logging.getLogger(__name__)


class ShellyLightController:
    """Shelly Light Controller."""

    def __init__(  # noqa: D107
        self,
        loop=None,
        port: int = PORT,
        ip_address: str = "",
        discovery_enabled: bool = False,
        discovery_interval: int = DISCOVERY_INTERVAL,
        update_enabled: bool = True,
        update_interval: int = UPDATE_INTERVAL,
        discovered_callback: Callable[[ShellyLight, bool], bool] | None = None,
        logger: logging.Logger | None = None,
    ) -> None:
        self._logger = logger or logging.getLogger(__name__)

        self._transport: Any = None
        self._protocol = None

        self._port = port
        self._ip_address = ip_address

        self._loop = loop or asyncio.get_running_loop()
        self._cleanup_done: asyncio.Event = asyncio.Event()
        self._discovery_enabled = discovery_enabled
        self._discovery_interval = discovery_interval
        self._update_enabled = update_enabled
        self._update_interval = update_interval
        self._num_of_zones: dict[int, ShellyLight] = {}

        self._light_discovered_callback = discovered_callback

        self._discovery_handle: asyncio.TimerHandle | None = None
        self._update_handle: asyncio.TimerHandle | None = None

        self._response_handler: dict[str, Callable] = {
            # GetNumOfInputsMessage: self._handle_num_inputs,
        }

    async def createConnection(self):
        """Create Connection."""

        self._transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        address = (self._ip_address, int(self._port))
        self._transport.connect(address)
        _LOGGER.log(logging.INFO, "Connected to %s", address)
        _LOGGER.log(logging.INFO, "Discover enabled %s", str(self._discovery_enabled))
        _LOGGER.log(logging.INFO, "Update enabled %s", str(self._update_enabled))

    async def start(self):
        """Start."""
        await self.createConnection()

    def send_update_message(self) -> None:
        """Send Update Message."""

        # if self._transport:
        # for d in self._registry.discovered_zones.values():
        # elf._send_update_message(d.zone_id)

        if self._update_enabled:
            self._update_handle = self._loop.call_later(
                self._update_interval, self.send_update_message
            )

    def cleanup(self) -> asyncio.Event:
        """Stop discovering. Stop updating. Close connection."""
        return self._cleanup_done

    def set_light_discovered_callback(
        self, callback: Callable[[ShellyLight, bool], bool] | None
    ) -> Callable[[ShellyLight, bool], bool] | None:
        """Set lights ihe Discovered callback."""
        old_callback = self._light_discovered_callback
        self._light_discovered_callback = callback
        return old_callback

    @property
    def discovered_zones(self) -> dict[int, ShellyLight]:
        """Return number of zones."""
        return self._num_of_zones

    @property
    def lights(self) -> list[ShellyLight]:
        """Return lights."""
        _LOGGER.log(logging.INFO, "controller lights")
        return list(self.discovered_zones.values())

    async def turn_on_off(self, zone_id: str, status: str):
        """Turn on off."""
