from ...tools import _Context
from ...utils.paras import Paras


class ToolsParas(Paras):

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
            'number_dict': {
                '0': '零',
                '1': '壹',
                '2': '贰',
                '3': '叁',
                '4': '肆',
                '5': '伍',
                '6': '陆',
                '7': '柒',
                '8': '捌',
                '9': '玖',
                '10': '拾',
                '100': '佰',
                '1000': '仟',
                '10000': '万',
                '100000000': '亿',
                '-1': '',
            }
        })
        return locals()