"""LEA Zone Structure."""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
import logging

_LOGGER = logging.getLogger(__name__)


class ShellyLight:
    """ShellyLight."""

    def __init__(self, controller, light_id: str) -> None:
        """Init."""
        self._controller = controller
        self._lastseen: datetime = datetime.now()
        self._model: str = ""
        self._turn_off: bool = False
        self._turn_on: bool = False
        self._light_id = light_id

        self._source: str = ""
        self._sourcesList: list[str] = []
        self._update_callback: Callable[[ShellyLight], None] | None = None
        self.is_manual: bool = False

    @property
    def update_callback(
        self,
    ) -> Callable[[ShellyLight], None] | None:
        """Get Update Callback."""
        return self._update_callback

    def set_update_callback(
        self,
        callback: Callable[[ShellyLight], None] | None,
    ) -> Callable[[ShellyLight], None] | None:
        """Set Update Callback."""
        old_callback = self._update_callback
        self._update_callback = callback
        return old_callback

    @property
    def controller(self):
        """Controller."""
        return self._controller

    @property
    def light_id(self) -> str:
        """Light Id."""
        return self._light_id

    @property
    def model(self) -> str:
        """Model."""
        return self._model

    @property
    def turn_on(self) -> bool:
        """turn_on."""
        return self._turn_on

    @property
    def turn_off(self) -> bool:
        """turn_off."""
        return self._turn_off

    @property
    def source(self) -> str:
        """Source."""
        return self._source

    @property
    def sourcesList(self) -> list[str]:
        """Sources list."""
        return self._sourcesList

    def update(self, value: str, commandType: str):
        """Update light."""
        # _LOGGER.log(logging.INFO, "update")
        _LOGGER.log(logging.INFO, "commandType:  %s", str(commandType))
        # _LOGGER.log(logging.INFO, "value:  %s", str(value))
        if commandType == "turn_on":
            # _LOGGER.log(logging.INFO, "update mute:  %s", str(value))
            if value == "true":
                self._turn_on = True
            else:
                self._turn_on = False

        self.update_lastseen()
        if self._update_callback and callable(self._update_callback):
            # _LOGGER.log(logging.INFO, "callback")
            self._update_callback(self)

    def update_lastseen(self) -> None:
        """Update Last Seen."""
        self._lastseen = datetime.now()
        # _LOGGER.log(logging.INFO, "last seen: %s", str(self._lastseen))

    async def set_light_on(self, _turn_on: bool) -> None:
        """Set Zone Power."""
        await self._controller.turn_on(self._light_id, str(_turn_on))
        self._turn_on = _turn_on

    async def set_light_off(self, _turn_off: bool) -> None:
        """Set Zone Power."""
        await self._controller.turn_off(self.light_id, str(_turn_off))
        self._turn_off = _turn_off
