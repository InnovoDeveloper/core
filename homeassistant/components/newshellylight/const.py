"""Constants for the ShellyLighting integration."""

from datetime import timedelta
from typing import Final

DOMAIN = "newshellylight"
MANUFACTURER = "Shelly"

CONF_MULTICAST_ADDRESS_DEFAULT = "239.255.255.250"
CONF_TARGET_PORT_DEFAULT = 4001
CONF_LISTENING_PORT_DEFAULT = 4002
CONF_DISCOVERY_INTERVAL_DEFAULT = 60
DISCOVERY_INTERVAL = 10
SCAN_INTERVAL = timedelta(seconds=60)
DISCOVERY_TIMEOUT = 10
UPDATE_INTERVAL = 3600
CONF_COAP_PORT: Final = "coap_port"
CONNECTION_TIMEOUT = 5  # seconds
PORT = 80
