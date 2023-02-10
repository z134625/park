from ....utils import paras
from ....tools import _Context


class IntellectParas(paras.Paras):
    @staticmethod
    def init() -> dict:
        context = _Context({
            'is_init': False,
            'setting_path': '',
            'reload_init': []
        })
        setting = _Context({})
        return locals()
