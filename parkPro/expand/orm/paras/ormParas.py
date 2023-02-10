from ....utils import paras
from ....tools import _Context


class ormParas(paras.Paras):
    @staticmethod
    def init() -> dict:
        _attrs = {
            'create_db': True,
            'cr': None,
            '_table': None
        }
        context = _Context({
            'host': '',
            'port': '',
            'user': '',
            'password': '',
            'dbname': False,
        })
        return locals()