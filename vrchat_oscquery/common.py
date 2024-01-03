import json
import socket
from typing import Callable
from zeroconf import ServiceInfo
from pythonosc.udp_client import SimpleUDPClient
from pythonosc.dispatcher import Dispatcher


def _oscjson_response(request_path: str, osc_port: int) -> str:
    """Super specific to VRChat hack for responding to the two requests it sends.

    VRChat will request the two paths:
    "/" To determine which osc paths to stream. We currently just request all data.
    "/?HOST_INFO" To determine where to stream data to.
    """
    obj = {}
    if request_path == "/?HOST_INFO":
        obj = {"OSC_PORT": osc_port}
    else:
        obj = {
            "CONTENTS": {
                "avatar": {"FULL_PATH": "/avatar"},
                "tracking": {"FULL_PATH": "/tracking"},
            }
        }
    return json.dumps(obj)


def _unused_port() -> int:
    """Returns an unused port."""
    sock = socket.socket()
    sock.bind(("", 0))
    return sock.getsockname()[1]


def _create_service_info(service_name: str, http_port: int) -> ServiceInfo:
    """Creates a zeroconf service config for the provided name/port."""
    return ServiceInfo(
        "_oscjson._tcp.local.",
        f"{service_name}._oscjson._tcp.local.",
        addresses=[socket.inet_aton("127.0.0.1")],
        port=http_port)


def vrc_client() -> SimpleUDPClient:
    """Convenience method for providing the default vrchat osc client."""
    return SimpleUDPClient("127.0.0.1", 9000)


def dict_to_dispatcher(routes: dict[str, Callable[[str, str], None]]) -> Dispatcher:
    """Convenince method for setting up a dispatcher."""
    d = Dispatcher()
    for route, handler in routes.items():
        d.map(route, handler)
    return d
