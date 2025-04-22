"""Controller."""

from __future__ import annotations

import asyncio
from collections.abc import Callable
import logging
import socket
from typing import Any

from .const import DISCOVERY_INTERVAL, PORT, UPDATE_INTERVAL
from .light import ShellyLight
from .rpc import send_rpc_request

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
        self._model: str = ""

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
        config = send_rpc_request(self._ip_address, "Shelly.GetConfig")
        self._num_of_zones = self.create_lights_from_config(self, config)
        if self._light_discovered_callback:
            for light in self._num_of_zones.values():
                self._light_discovered_callback(light, True)

    def create_lights_from_config(
        self, controller, config: dict
    ) -> dict[int, ShellyLight]:
        """Create Light Entities."""
        lights = {}
        for key, value in config.items():
            if key.startswith("switch:"):
                switch_id = int(key.split(":")[1])
                light = ShellyLight(controller, str(switch_id), value)
                # light._model = config["sys"]["mac"]
                # Set state
                light.update(
                    "true" if value["initial_state"] == "on" else "false", "turn_on"
                )
                lights[switch_id] = light
        return lights

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

    async def turn_on(self, light_id: str, _value: str):
        """Turn on."""
        send_rpc_request(
            self._ip_address, "Switch.Set", {"id": int(light_id), "on": True}
        )

    async def turn_off(self, light_id: str, _value: str):
        """Turn Off."""
        send_rpc_request(
            self._ip_address, "Switch.Set", {"id": int(light_id), "on": False}
        )

    @property
    def model(self) -> str:
        """Get model."""
        return self._model

    @model.setter
    def model(self, value: str) -> None:
        """Set model."""
        self._model = value

    @property
    def lights(self) -> list[ShellyLight]:
        """Return lights."""
        _LOGGER.log(logging.INFO, "controller lights")
        return list(self._num_of_zones.values())

    async def turn_on_off(self, zone_id: str, status: str):
        """Turn on off."""
