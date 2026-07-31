import asyncio
from aiohttp import web
from zeroconf.asyncio import AsyncZeroconf
from vrchat_oscquery.common import _unused_port,  _oscjson_response, _create_service_info
import json
import os


class Proxy:
    def __init__(self, name: str, port: int):
        self.name = name
        self.port = port
        self.root_req = False  # Have we sent the response for /
        self.host_req = False  # Have we sent the response for /?HOST_INFO
        self.http_server = web.Application()
        self.http_server.add_routes([web.get("/", self.handle_request)])
        self.runner = web.AppRunner(self.http_server)

    async def forward(self):
        print(f"[Start] {self.name}")
        await AsyncZeroconf().async_register_service(_create_service_info(self.name, self.port))
        await self.runner.setup()
        site = web.TCPSite(self.runner, "127.0.0.1", self.port)
        await site.start()
        await self.shutdown_after_delivery()

    def handle_request(self, req: web.Request):
        if req.path_qs == "/":
            self.root_req = True
        elif req.path_qs == "/?HOST_INFO":
            self.host_req = True

        return web.Response(body=_oscjson_response(req.path_qs, self.port))

    async def shutdown_after_delivery(self):
        while True:
            await asyncio.sleep(1)
            if self.root_req and self.host_req:
                print(f"[Ready] {self.name}")
                await self.http_server.shutdown()
                return


def main():
    if not os.path.exists("config.json"):
        print("No config.json. Created one. Add your osc services to it and rerun.")
        with open("config.json", "w") as o:
            json.dump({
                "My Osc app": 1234,
                "My other Osc app": 1235,
            }, o, indent=2)
    else:
        with open("config.json", "r") as i:
            routines = []
            for name, port in json.load(i).items():
                routines.append(Proxy(name, port).forward())
            asyncio.get_event_loop().run_until_complete(asyncio.gather(*routines))


if __name__ == "__main__":
    main()
