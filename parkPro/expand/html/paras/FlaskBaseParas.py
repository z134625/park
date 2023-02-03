from ....utils import paras
from ....tools import _Context


class FlaskBaseParas(paras.Paras):
    @staticmethod
    def init() -> dict:
        _error = False
        _attrs = {
            'setting_path': '',
        }
        context = _Context({
            'app': None,
            'request': None,
            'is_init': False,
            'host': '127.0.0.1',
            'port': 5000,
        })
        flags = {'flask_route_flag': True}
        return locals()
