import os
import uuid

from flask import (
    Flask,
    request,
    render_template,
    url_for,
    make_response
)
from types import (
    FunctionType,
    MethodType,
    LambdaType
)
from typing import Union, Any
from flask_cors import CORS

from ...utils import (
    base,
    api
)
from ...tools import mkdir, remove, listPath
from .paras import FlaskBaseParas
from .. import setting


class FlaskBase(base.ParkLY):
    _name = 'flask'
    _inherit = 'tools'
    paras = FlaskBaseParas()

    def flask_init(
            self
    ):
        pass

    def init_setting(
            self,
    ) -> bool:
        if not self.paras.context.is_init:
            self.flask_init()
            self.context.update({
                'app': Flask(__name__),
                'is_init': True,
                'old_html': '',
            })
            self.port()
            self.host()
            CORS(self.context.app, resources=r'/*')
            return True

    @api.monitor(fields={api.MONITOR_ORDER_BEFORE: 'init_setting', api.MONITOR_ORDER_AFTER: 'load'},
                 after_args='images',
                 ty=api.MONITOR_FUNC,
                 order=api.MONITOR_ORDER_BEFORE)
    def _flask_route_flag(
            self,
            func: Union[FunctionType, MethodType]
    ) -> Union[FunctionType, MethodType]:
        if hasattr(func, 'flask_route_flag'):
            route_func = self.context.app.route(*func.flask_route_flag['args'],
                                                **func.flask_route_flag['kwargs']
                                                )(self._log_route(func))
            return route_func
        return func

    def _log_route(
            self,
            func
    ):
        func_str = """
def {func_name}(*args, **kwargs):
    url = request.url
    try:
        res = func(*args, **kwargs)
        env.log.debug(f'[%s] %s : 成功' % (url, request.method))
        return res
    except Exception as e:
        env.log.error(f'[%s] %s : %s' % (url, request.method, str(e)))
        raise e
        """.format(func_name=func.__name__)
        new_func = compile(func_str, '', 'exec')
        return FunctionType(new_func.co_consts[0], {'env': self.env, 'request': request, 'func': func})

    @api.command(
        keyword=['--start'],
        name='run',
        unique=True,
        priority=10
    )
    def run(
            self
    ) -> None:
        assert self.context.app
        try:
            print()
            self.context.app.run(host=self.context.host, port=self.context.port)
        finally:
            self.save('log', args=('flask_log',))
            self.delete_cache()

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
        obj = object()
        settings = self.env['setting'].load('setting', args=path).give(obj)
        for key, value in settings.items():
            setting.var[key] = value
        del obj

    def render(
            self,
            html: str = None,
            **kwargs
    ) -> str:
        url_rule = request.url_rule.rule
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
            html_name = uuid.uuid4().hex + '.html'
            if os.path.exists(html):
                html_name = os.path.basename(html)
                html = self.open(html, mode='r')
            html = self.load('js_or_css', args={
                'path': js_paths + css_paths + self.js_paths_gl + self.css_paths_gl,
                'html': html
            })
            self.context.update({
                'old_html': html
            })
        else:
            html_name = 'index.html'
            html = self.load('js_or_css', args={
                'path': js_paths + css_paths + self.js_paths_gl + self.css_paths_gl,
                'html': self.context.old_html
            })
        base_path = os.path.join(os.path.dirname(__file__), 'templates')
        base_name = os.path.join(base_path, html_name)
        mkdir(base_path)
        if not os.path.exists(base_name):
            self.open(base_name, mode='w', datas=html)
        if html != self.context.old_html:
            base_name = self.exists_rename(base_name)
            self.open(base_name, mode='w', datas=html)
        if base_name not in self.cache_path and self.cache_path != 'all':
            self.context.cache_files.append(base_name)
        return render_template(os.path.basename(base_name), **kwargs)

    def _load_js_or_css(
            self,
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
                cache_path = os.path.join(base_path, two_level_name)
                if not os.path.exists(cache_path):
                    self.open(cache_path, mode='w', datas=file)
            else:
                continue
            if cache_path not in self.cache_path and self.cache_path != 'all':
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
        jquery = f"""<script type="text/javascript" src="https://code.jquery.com/jquery-3.6.3.min.js"></script>"""
        if isinstance(html, str):
            html = html.replace('</html>', f'   {js_paths}\n</html>')
            return html.replace('</head>', f'   {jquery}\n</head>')
        elif isinstance(html, bytes):
            return html.decode('utf-8').replace('</html>', f'   {js_paths}\n</html>')
        else:
            return html

    def Response(
            self, html,
            delete: bool = False,
            timeout: int = None,
            cookies: Union[dict, str] = None,
            **kwargs):
        res = make_response(self.render(html=html, **kwargs))
        if cookies is None:
            cookies = {}
        elif cookies == 'all' and delete:
            cookies = dict(request.cookies)
        for k, v in cookies.items():
            if not delete:
                if k == 'time':
                    v = str(int(v))
                res.set_cookie(k, v, max_age=timeout)
            else:
                res.delete_cookie(k)
        return res

    def _load_images(
            self
    ):
        if not self.paras.context.is_load_images:
            base_path = os.path.join(os.path.dirname(__file__), 'static')
            paths = self.images_path
            images = []
            if os.path.isdir(paths):
                images = listPath(paths, suffix=['BMP', 'JPG', 'JPEG', 'JPEG', 'GIF'], splicing=True)
            elif os.path.isfile(paths):
                images = [paths]
            for image in images:
                file_name = os.path.basename(image)
                file = self.open(image, mode='rb')
                base_path = os.path.join(base_path, 'images')
                mkdir(base_path)
                path = os.path.join(base_path, file_name)
                if not os.path.exists(path):
                    self.open(path, mode='wb', datas=file)
                    if image not in self.cache_path and self.cache_path != 'all':
                        self.context.cache_files.append(path)
            self.context.update({
                'is_load_images': True,
            })
