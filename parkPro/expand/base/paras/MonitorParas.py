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
            'monitor_before_fields': set(),
            'monitor_after_fields': set(),
            'monitor_before_func': {},
            'monitor_after_func': {},
            'monitor_func_before_args': {},
            'monitor_func_after_args': {},
        })
        flags = {'monitor_flag': True}
        return locals()