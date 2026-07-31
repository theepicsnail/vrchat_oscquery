
from zeroconf import Zeroconf
from pythonosc.dispatcher import Dispatcher
import socket
import threading
from pythonosc.osc_server import ThreadingOSCUDPServer
from http.server import BaseHTTPRequestHandler, HTTPServer
from .common import _oscjson_response, _create_service_info, _get_app_host


def vrc_osc(name: str, dispatcher: Dispatcher, foreground=False):
    """Connects vrchat to the provided dispatcher.

    Foreground:
        False (default) = We run the server in the background.
        True = We block the main thread here, ctrl-c to interrupt it.
    """

    host = _get_app_host()

    osc_server = ThreadingOSCUDPServer((host, 0), dispatcher)
    osc_port = osc_server.socket.getsockname()[1]

    class OSCJsonHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(_oscjson_response(self.path, osc_port).encode())

    httpd = HTTPServer((host, 0), OSCJsonHandler)
    http_port = httpd.socket.getsockname()[1]
    Zeroconf().register_service(_create_service_info(name, http_port))

    threading.Thread(target=osc_server.serve_forever, daemon=True).start()

    if foreground:
        httpd.serve_forever()
    else:
        threading.Thread(target=httpd.serve_forever, daemon=True).start()
        return httpd
