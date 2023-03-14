
import os

from ...utils import (
    base,
    api
)
from ...tools import remove
from .paras import WebParas


class WebSocket(base.ParkLY):
    _name = 'web'
    _inherit = 'tools'
    paras = WebParas()

    @api.command(
        keyword=['--delete'],
        name='delete_cache',
        unique=True,
        priority=-1
    )
    def delete_all_cache(self):
        static_path = os.path.join(os.path.dirname(__file__), 'static')
        templates_path = os.path.join(os.path.dirname(__file__), 'templates')
        remove(static_path)
        remove(templates_path)

    def delete_cache(
            self
    ):
        for file in self.context.cache_files:
            if os.path.exists(file):
                remove(file)

    @api.command(
        keyword=['-p', '--port'],
        name='port',
        unique=True,
        priority=0
    )
    def port(
            self,
            port: int = 5000
    ) -> None:
        self.context.port = int(port)

    @api.command(
        keyword=['-h', '--host'],
        name='host',
        unique=True,
        priority=0,
    )
    def host(
            self,
            host: str = '127.0.0.1'
    ) -> None:
        self.context.host = host

    @api.command(
        keyword=['-c', '--config'],
        name='path',
        unique=True,
        priority=0,
    )
    def path(self,
             path: str
             ) -> None:
        self.setting_path = path
