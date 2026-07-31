import asyncio
from aiohttp import web
from zeroconf.asyncio import AsyncZeroconf
from pythonosc.osc_server import AsyncIOOSCUDPServer
from pythonosc.dispatcher import Dispatcher
from .common import _oscjson_response, _create_service_info, _get_app_host


async def vrc_osc(name: str, dispatcher: Dispatcher, foreground=False):
    host = _get_app_host()

    # Setup OSC server on a free port.
    osc_server = AsyncIOOSCUDPServer(
        (host, 0), dispatcher, asyncio.get_event_loop())
    osc_transport, _osc_protocol = await osc_server.create_serve_endpoint()
    _osc_host, osc_port = osc_transport.get_extra_info("sockname")

    # Setup OscQuery server on a free port.
    app = web.Application()

    def req_handler(req):
        return web.Response(body=_oscjson_response(req.path_qs, osc_port))

    app.add_routes([web.get("/", req_handler)])
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host, 0)
    await site.start()

    # Setup ZeroConf to announce the OscQuery server.
    await AsyncZeroconf().async_register_service(_create_service_info(name, site.port))

    if foreground:
        await asyncio.gather(*asyncio.all_tasks())
