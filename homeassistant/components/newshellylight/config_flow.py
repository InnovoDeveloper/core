"""Config flow for Shelly Light integration."""

from __future__ import annotations

import json
import logging
import socket

# import requests
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.config_entries import ConfigFlowResult
from homeassistant.exceptions import ConfigEntryNotReady

from .const import DOMAIN

PORT = 80
_LOGGER = logging.getLogger(__name__)


class ShellyConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Shelly Light."""

    def __init__(self) -> None:
        """Init."""

        self.data: dict[str, str] = {}

    async def async_step_user(self, user_input=None) -> ConfigFlowResult:
        """Step User."""
        # host = CONF_HOST
        host = user_input
        # Specify items in the order they are to be displayed in the UI
        try:
            if user_input is not None:
                # ip_address = user_input["IP Address"]

                deviceName = getDeviceName(user_input["IP Address"])
                _LOGGER.log(logging.INFO, "deviceName %s", str(deviceName))
                # if not deviceName:
                # _LOGGER.log(logging.INFO, "deviceName %s", str(deviceName))
                # raise ConfigEntryNotReady

                # return self.async_create_entry(title=deviceName, data=user_input)
                return self.async_create_entry(
                    title=f"Shelly @ {host}", data=user_input
                )
            return self.async_show_form(
                step_id="user",
                data_schema=vol.Schema(
                    {
                        vol.Required("IP Address"): str,
                    }
                ),
            )
        except ConfigEntryNotReady:
            self.data["base"] = "cannot connect"
            return self.async_show_form(step_id="user", errors=self.data)


def getDeviceName(ip_address):
    """Get Shelly Gen1 Device Name via raw TCP HTTP."""
    msg = f"GET /settings HTTP/1.1\r\nHost: {ip_address}\r\nConnection: close\r\n\r\n"

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(5)
            s.connect((ip_address, PORT))
            s.sendall(msg.encode())

            response = b""
            while True:
                try:
                    part = s.recv(2048)
                    if not part:
                        break
                    response += part
                except TimeoutError:
                    break

        response_str = response.decode(errors="ignore")
        _LOGGER.info("Raw response from device: %s", response_str)

        if "\r\n\r\n" in response_str:
            json_data = response_str.split("\r\n\r\n", 1)[1]
            try:
                parsed = json.loads(json_data)
                return parsed.get("name", "Shelly Device")
            except json.JSONDecodeError:
                _LOGGER.warning("Failed to parse JSON from Shelly: %s", json_data)
                return None
    except (TimeoutError, OSError, ConnectionRefusedError) as e:
        _LOGGER.warning("Could not connect to Shelly device at %s: %s", ip_address, e)
        return None
