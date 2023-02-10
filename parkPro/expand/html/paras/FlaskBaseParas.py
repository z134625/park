from ....utils import paras
from ....tools import _Context


class FlaskBaseParas(paras.Paras):
    @staticmethod
    def init() -> dict:
        _error = False
        _attrs = {
            'setting_path': '',
            'js_paths': [],
            'css_paths': [],
            'image_paths': [],
            'js_paths_gl': [],
            'css_paths_gl': [],
            'image_paths_gl': [],

        }
        context = _Context({
            'app': None,
            'request': None,
            'is_init': False,
            'host': '127.0.0.1',
            'port': 5000,
            'cache_files': [],
            'user_dict': {},
            'user_list': [],
        })
        flags = {'flask_route_flag': True}
        return locals()
