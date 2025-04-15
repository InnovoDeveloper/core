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
    """Get Shelly Gen2 device name using Shelly.GetConfig RPC."""

    body = "{}"
    encoded_body = body.encode()

    request = (
        f"POST /rpc/Shelly.GetConfig HTTP/1.1\r\n"
        f"Host: {ip_address}\r\n"
        "Content-Type: application/json\r\n"
        f"Content-Length: {len(encoded_body)}\r\n"
        "Connection: close\r\n"
        "\r\n"
    ).encode() + encoded_body

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(5)
        s.connect((ip_address, 80))
        s.sendall(request)

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
            _LOGGER.info("Parsed JSON from device: %s", parsed)
            return parsed.get("device", {}).get("name", "Shelly Device")
        except json.JSONDecodeError:
            _LOGGER.warning("Failed to parse JSON: %s", json_data)
            return None
    return None
