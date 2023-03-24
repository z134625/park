from ...tools import _Context
from ...utils.paras import Paras


class SpiderParas(Paras):

    @staticmethod
    def init():
        context = _Context({
            '_': 1,
            'method': 'GET',
            '_method': 'GET',
            'url': '',
            '_url': '',
            'error_url': [],
            'items': {},
            'headers': {},
        })
        return locals()