import warnings
import re
from collections.abc import Iterable
from inspect import isclass, isfunction

from .utils.data import Compare, VersionCompare
from .conf.setting import PythonVersion
from .conf.setting import ParkConcurrency
from .utils import _Park

__version__ = "1.7.1"
__name__ = "park"

python_version = re.split(r'[|\s]', PythonVersion)
if ">=" not in Compare(VersionCompare(python_version[0]), VersionCompare("3.10.0")):
    warnings.warn("当前python版本低于要求版本(3.10.0)，可能会有未知错误", RuntimeWarning, stacklevel=2)


class Park(_Park):

    def __init__(self):
        pass

    @classmethod
    def _register_function(cls, func=None, call: bool = False, **kwarg):
        is_call = call
        func_arg = kwarg.get('arg', None)
        queue_task = kwarg.get('task', False)
        func_name = func.__name__
        if hasattr(func, '_name'):
            func_name = func._name

        func_obj = tuple()
        if not queue_task:
            if is_call and func_arg:
                if isinstance(func_obj, dict):
                    func_obj = func(**func_arg)
                else:
                    func_obj = func(*func_arg)
            elif is_call:
                func_obj = func()
            func_result = {
                'number': cls._register_number,
                'func': func,
                'func_obj': func_obj,
                'args': func_arg,
                'info': {
                    'module': func.__module__,
                    'doc': func.__doc__,
                    'name': func.__name__,
                },
                'process': None,
            }
        else:
            func_result = {

            }
        if isclass(func):
            cls._register_apps[func_name + '_' + str(cls._register_number)] = func_result
            cls._register_number += 1
        elif isfunction(func):
            cls._register_funcs[func_name + '_' + str(cls._register_number)] = func_result
            cls._register_number += 1

    def register(self, apps, kwargs):
        if type(apps).__name__ == 'module':
            index = dir(apps).index('__builtins__')
            funcs = dir(apps)[:index]
            for func in funcs:
                self._register_function(app=eval(f'apps.{func}'), **kwargs)
        else:
            if isinstance(apps, Iterable):
                for app in apps:
                    if type(app).__name__ == 'module':
                        index = dir(apps).index('__builtins__')
                        funcs = dir(apps)[:index]
                        for func in funcs:
                            self._register_function(app=eval(f'apps.{func}'), **kwargs)
                    else:
                        self._register_function(app=app, **kwargs)
            else:
                self._register_function(app=apps, **kwargs)


park = Park()
registers = park.register
