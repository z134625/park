from ....utils import paras
from ....tools import _Context


class FlaskBaseParas(paras.Paras):
    @staticmethod
    def init() -> dict:
        ERROR = False
        ATTRS = {
            'js_paths': [],
            'css_paths': [],
            'images_path': [],
            'js_paths_gl': [],
            'css_paths_gl': [],
            'cache_path': 'all',
        }
        context = _Context({
            'app': None,
            'request': None,
            'is_init': False,
            'is_load_images': False,
        })
        flags = {'flask_route_flag': True}
        return locals()
