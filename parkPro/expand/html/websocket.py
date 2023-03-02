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
