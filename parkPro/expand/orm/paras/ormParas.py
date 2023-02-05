from ....utils import paras
from ....tools import _Context


class ormParas(paras.Paras):
    @staticmethod
    def init() -> dict:
        _attrs = {
            'create_db': True,
        }
        context = _Context({
            'host': '',
            'port': '',
            'user': '',
            'password': '',
            'dbname': False,
            'cr': ''
        })
        return locals()