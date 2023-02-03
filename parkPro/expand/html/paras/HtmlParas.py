from ....utils import paras


class HtmlParas(paras.Paras):
    @staticmethod
    def init() -> dict:
        _attrs = {
            'is_init': False,
        }
        return locals()
