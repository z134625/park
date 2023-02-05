from ....utils.paras import Paras
from ....tools import _Context


class CommandParas(Paras):
    """
    工具配置
    """

    @staticmethod
    def init():
        _root = True
        context = _Context({
            'command_info': {
                'help': '',
                'func': '',
                'unique': True,
                'priority': -1,
                'name': '',
            },
            'command_keyword': {},
            'ext_bar': ['-', r'\\', '|', '/'],
            'command_k_2_args': {},
            'command_k_true': [],
        })
        flags = {'command_flag': True}
        return locals()