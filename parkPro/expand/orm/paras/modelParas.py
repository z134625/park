from ....utils import paras


class modelParas(paras.Paras):
    @staticmethod
    def init() -> dict:
        _attrs = {
            '_fields': {},
            'fields': {},
            'is_init': False
        }
        return locals()
