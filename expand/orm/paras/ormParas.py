from parkPro.utils import paras
from parkPro.tools import _Context


class ormParas(paras.Paras):
    @staticmethod
    def init() -> dict:
        ATTRS = {
            'cr': None,
            'connection': None
        }
        return locals()