import asyncio
import websockets


from typing import Union, Any
from flask_cors import CORS

from ...utils import (
    base,
    api
)
from ...tools import mkdir, remove, listPath
from .paras import FlaskBaseParas


class WebSocket(base.ParkLY):
    _name = 'web.socket'

    @staticmethod
    async def _server(host, port):
        uri = f'ws/{host}:{port}'
        conn_handler = await websockets.connect(uri)
        await conn_handler.send(uri)
        while True:
            response = await conn_handler.recv()


