from ....utils.paras import Paras
from ....tools import _Context


class MonitorParas(Paras):
    """
    监控方法的配置，
    默认将添加_return 参数，
    该参数用于获取被监控方法的返回值
    """
    ban = ['_error', 'context', '_root']

    @staticmethod
    def init():
        _error = False
        _root = True
        _warn = False
        context = _Context({
            'return_result': False,
            'funcName': None,
            'monitor_fields': set(),
            'monitor_func': {},
            'monitor_func_args': {}
        })
        return locals()