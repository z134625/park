from ....utils import paras
from ....tools import _Context


class ormParas(paras.Paras):
    @staticmethod
    def init() -> dict:
        ATTRS = {
            'cr': None,
            'connection': None
        }
        return locals()