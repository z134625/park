
import os

from flask import (
    Flask,
    request,
    redirect,
    render_template,
    url_for
)
from types import (
    FunctionType,
    MethodType,
    LambdaType
)
from typing import Union, Any

from ...utils import (
    base,
    api
)
from ...tools import mkdir, remove
from .paras import FlaskBaseParas


class FlaskBase(base.ParkLY):
    _name = 'flask'
    _inherit = 'tools'
    paras = FlaskBaseParas()

    def flask_init(self):
        pass

    def init_setting(self,
                     path: str
                     ) -> None:
        if not self.paras.context.is_init:
            self.flask_init()
            self.env['setting'].load('setting', args=(path or self.setting_path, )).give(self)
            self.context.update({
                'app': Flask(__name__),
                'request': request,
                'is_init': True,
                'redirect': redirect,
                'render_template': render_template,
                'old_html': '',
                'url_for': url_for,
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
                                                )(self._log_route(func))
            return route_func
        return func

    def _log_route(self, func):
        def warp(*args, **kwargs):
            url = self.context.request.url
            try:
                res = func(*args, **kwargs)
                self.env.log.debug(f'[{url}] {self.context.request.method} : 成功')
                return res
            except Exception as e:
                self.env.log.error(f'[{url}] {self.context.request.method} : {str(e)}')
                raise e
        return warp

    @api.command(keyword=['--start'],
                 name='run',
                 unique=True,
                 priority=10
                 )
    def run(self) -> None:
        assert self.context.app
        try:
            print()
            self.context.app.run(host=self.context.host, port=self.context.port)
        finally:
            self.save('log', args=('flask_log', ))
            self.delete_cache()

    def delete_cache(self):
        for file in self.context.cache_files:
            if os.path.exists(file):
                remove(file)

    @api.command(keyword=['-p', '--port'],
                 name='port',
                 unique=True,
                 priority=0
                 )
    def port(self,
             port: int = 5000
             ) -> None:
        self.context.port = port

    @api.command(keyword=['-h', '--host'],
                 name='host',
                 unique=True,
                 priority=0,
                 )
    def host(self,
             host: str = '127.0.0.1'
             ) -> None:
        self.context.host = host

    @api.command(keyword=['-p', '--path'],
                 name='path',
                 unique=True,
                 priority=0,
                 )
    def path(self,
             path: str
             ) -> None:
        self.setting_path = path

    def render(self,
               html: str = None,
               **kwargs
               ) -> bytes:
        url_rule = self.context.request.url_rule.rule
        js_paths = []
        css_paths = []
        if isinstance(self.js_paths, (list, tuple)):
            js_paths = self.js_paths
        elif isinstance(self.js_paths, dict):
            js_paths = self.js_paths.get(url_rule, [])

        if isinstance(self.css_paths, (list, tuple)):
            css_paths = self.css_paths
        elif isinstance(self.css_paths, dict):
            css_paths = self.css_paths.get(url_rule, [])
        if html:
            if os.path.exists(html):
                html = self.open(html, mode='r')
            html = self.load('js_or_css', args={
                'path': js_paths + css_paths + self.js_paths_gl + self.css_paths_gl,
                'html': html
            })
            self.context.update({
                'old_html': html
            })
        else:
            html = self.load('js_or_css', args={
                'path': js_paths + css_paths + self.js_paths_gl + self.css_paths_gl,
                'html': self.context.old_html
            })
        base_path = os.path.join(os.path.dirname(__file__), 'templates')
        base_name = self.exists_rename(os.path.join(base_path, 'index.html'))
        mkdir(base_path)
        self.open(base_name, mode='w', datas=html)
        self.context.cache_files.append(base_name)
        return self.context.render_template(os.path.basename(base_name), **kwargs)

    def _load_js_or_css(self,
                        path: Any,
                        html: Union[str, bytes]
                        ) -> Union[str, bytes]:
        paths = []
        if isinstance(path, str):
            paths = [path]
        elif isinstance(path, (list, tuple)):
            paths = path
        elif isinstance(path, LambdaType) or callable(path):
            paths = path(self)
        js_paths = []
        base_path = os.path.join(os.path.dirname(__file__), 'static')
        old_sep = os.sep
        os.sep = '/'
        for path in paths:
            if os.path.exists(path):
                file = self.open(path, mode='r')
                two_level = os.path.splitext(path)[1].replace('.', '')
                mkdir(os.path.join(base_path, two_level))
                two_level_name = os.path.join(two_level, os.path.basename(path))
                cache_path = self.exists_rename(os.path.join(base_path, two_level_name))
                self.open(cache_path, mode='w', datas=file)
            else:
                continue
            self.context.cache_files.append(cache_path)
            url = url_for('static', filename=two_level_name)
            if os.name == 'nt':
                url = url.replace('%5C', '/')
            if not path.endswith('js'):
                js_path = f"""<link type="text/css" rel="stylesheet" href="{url}">"""
            else:
                js_path = f"""<script type="text/javascript" src="{url}"></script>"""
            js_paths.append(js_path)
        js_paths = '\n'.join(js_paths)
        os.sep = old_sep
        if isinstance(html, str):
            return html.replace('</head>', f'   {js_paths}\n</head>')
        elif isinstance(html, bytes):
            return html.decode('utf-8').replace('</head>', f'   {js_paths}\n</head>')
        else:
            return html

    def _load_images(self):
        pass
