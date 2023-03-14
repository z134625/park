from ....utils import paras
from ....tools import _Context


class WebParas(paras.Paras):
    @staticmethod
    def init() -> dict:
        ERROR = False
        context = _Context({
            'is_init': False,
            'host': '127.0.0.1',
            'port': 5000,
            'cache_files': [],
            'user_dict': {},
            'user_list': [],
        })
        return locals()