"""Config flow for Shelly Light integration."""

from __future__ import annotations

import logging
import socket

import requests
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
    """Get Device Name."""
    _LOGGER.log(logging.INFO, "getDeviceName")
    _LOGGER.log(logging.INFO, "Connect to %s", ip_address)
    # msg = "get /rpc/Shelly.GetConfig\n"
    mySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Define the URL you want to send a GET request to
    # url = f"http://{ip_address}/rpc/Shelly.GetConfig"
    msg = "get settings\n"

    address = (ip_address, int(PORT))
    try:
        mySocket.connect(address)
        mySocket.send(msg.encode())
        # while True:
        data = mySocket.recv(2048)
        # Send the GET request
        # response = requests.get(url, timeout=5)
        _LOGGER.log(logging.INFO, "response data: %s", str(data))

        if data:
            _LOGGER.log(logging.INFO, "response data: %s", str(data))
            data = data.decode()
            # deviceName = "ShellyDevice"

            # return deviceName
        # Check if the request was successful (status code 200)
    # if response.status_code == 200:
    # Parse the JSON response
    # data = response.json()
    # _LOGGER.log(logging.INFO, "response data: %s", str(data))
    # else:
    # _LOGGER.log(logging.INFO, "response data: %s", response.status_code)
    except requests.RequestException:
        # in your case, ip address: shelly ip, port: 80
        # msg = "get /settings\n"
        address = (ip_address, PORT)
    try:
        mySocket.connect(address)
        mySocket.send(msg.encode())
        # while True:
        data = mySocket.recv(2048)
        _LOGGER.log(logging.INFO, "response data: %s", str(data))

        if data:
            _LOGGER.log(logging.INFO, "response data: %s", str(data))
            data = data.decode()
            # deviceName = data.replace("/amp/deviceInfo/deviceName", "")
            # deviceName = deviceName.replace("\n", "")
            # deviceName = deviceName.replace('"', "")
            data = "test"
            mySocket.close()

            return ""
    except (TimeoutError, OSError, ConnectionRefusedError):
        return False
    finally:
        mySocket.close()
