import jinja2

from flask import (
    Flask,
    request,
    redirect,
    render_template
)
from types import (
    FunctionType,
    MethodType
)
from typing import Union

from ...utils import (
    base,
    api
)
from .paras import FlaskBaseParas


class FlaskBase(base.ParkLY):
    _name = 'flask'
    _inherit = 'tools'
    paras = FlaskBaseParas()

    def init_setting(self,
                     path: str
                     ) -> None:
        if not self.paras.context.is_init:
            self.env['setting'].open(path).give(self)
            self.context.update({
                'app': Flask(__name__),
                'request': request,
                'is_init': True,
                'redirect': redirect,
                'render_template': render_template,
                'old_html': '',
                'render': self.render
            })
            self.port()
            self.host()

    @api.monitor(fields='init_setting',
                 args=lambda x: x.setting_path,
                 ty=api.MONITOR_FUNC,
                 order=api.MONITOR_ORDER_BEFORE)
    def _flask_route_flag(self,
                          func: Union[FunctionType, MethodType]
                          ) -> Union[FunctionType, MethodType]:
        if hasattr(func, 'flask_route_flag'):
            route_func = self.context.app.route(*func.flask_route_flag['args'],
                                                **func.flask_route_flag['kwargs']
                                                )(func)
            return route_func
        return func

    @api.command(keyword=['--start'],
                 unique=True,
                 priority=10
                 )
    def run(self) -> None:
        assert self.context.app
        try:
            print()
            self.context.app.run(host=self.context.host, port=self.context.port)
        finally:
            self.save_log()

    @api.command(keyword=['-p', '--port'],
                 unique=True,
                 priority=0
                 )
    def port(self,
             port: int = 5000
             ) -> None:
        self.context.port = port

    @api.command(keyword=['-h', '--host'],
                 unique=True,
                 priority=0,
                 )
    def host(self,
             host: str = '127.0.0.1'
             ) -> None:
        self.context.host = host

    @api.command(keyword=['-p', '--path'],
                 unique=True,
                 priority=0,
                 )
    def path(self,
             path: str
             ) -> None:
        self.setting_path = path

    def render(self, html=None, **kwargs):
        if html:
            temp = jinja2.Template(html)
            self.context.update({
                'old_html': html
            })
        else:
            temp = jinja2.Template(self.context.old_html)
        response = temp.render(**kwargs).encode('utf-8')
        return response
