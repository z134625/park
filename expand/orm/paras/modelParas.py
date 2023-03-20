from parkPro.utils import paras


class modelParas(paras.Paras):
    @staticmethod
    def init() -> dict:
        ATTRS = {
            '_fields': {},
            'fields': {},
            'is_init': False
        }
        return locals()
