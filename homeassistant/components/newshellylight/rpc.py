"""Rpc file."""

import json
import logging
import socket

_LOGGER = logging.getLogger(__name__)


def send_rpc_request(ip_address: str, method: str, params: dict | None = None) -> dict:
    """Send RPC request to Shelly device and return parsed JSON response."""
    body = {
        "id": 1,
        "method": method,
        "params": params or {},
    }
    encoded_body = json.dumps(body).encode()

    request = (
        f"POST /rpc/{method} HTTP/1.1\r\n"
        f"Host: {ip_address}\r\n"
        "Content-Type: application/json\r\n"
        f"Content-Length: {len(encoded_body)}\r\n"
        "Connection: close\r\n"
        "\r\n"
    ).encode() + encoded_body

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(5)
            s.connect((ip_address, 80))
            s.sendall(request)
            response_bytes = b""
            while True:
                chunk = s.recv(4096)
                if not chunk:
                    break
                response_bytes += chunk

        # Split HTTP header and body
        _, body_bytes = response_bytes.split(b"\r\n\r\n", 1)
        body_str = body_bytes.decode(errors="ignore")  # decode bytes to str

        response_json = json.loads(body_str)  # parse JSON string to dict

        if "result" in response_json:
            return response_json["result"]

        return response_json  # fallback if no "result" key  # noqa: TRY300

    except Exception as e:  # noqa: BLE001
        _LOGGER.error("Error sending RPC request to %s: %s", ip_address, e)
        return {}
