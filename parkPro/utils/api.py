import datetime
import time

from decimal import Decimal
from types import (
    MethodType,
    FunctionType,
    LambdaType
)
from typing import (
    Union,
    Tuple,
    List,
    Callable,
    Any, Optional
)

MONITOR_VAR = 0
MONITOR_FUNC = 1
MONITOR_ORDER_AFTER = 0
MONITOR_ORDER_BEFORE = 1


def command(
        keyword: Union[str, Tuple[str], List[str]],
        unique: bool = False,
        priority: int = -1
) -> Callable[[Any], Any]:
    def warp(
            func: Union[MethodType, FunctionType]
    ) -> Union[Any]:
        setattr(func, 'command_flag', {
            'keyword': keyword,
            'unique': unique,
            'priority': priority,
        })
        return func

    return warp


def monitor(
        fields: Union[str, Tuple[str], List[str]],
        args: Union[Tuple[Tuple, dict], Tuple[Any], LambdaType, None, Any] = None,
        ty: int = MONITOR_FUNC,
        order: int = MONITOR_ORDER_AFTER
) -> Callable[[Any], Any]:
    def warp(func):
        setattr(func, 'monitor_flag', {
            'fields': fields,
            'args': args or ((), {}),
            'type': ty,
            'order': order,
        })
        return func

    return warp


def reckon_by_time_run(
        func: Optional[Callable]
) -> Optional[Callable]:
    if callable(func):
        return setattr(func, 'reckon_by_time_run', True) or func
    return func


def flask_route(
        *args,
        **kwargs
) -> Optional[Callable]:
    def warp(
            func: Optional[Callable]
    ) -> Optional[Callable]:
        setattr(func, 'flask_route_flag', {
            'args': args,
            'kwargs': kwargs,
        })
        return func

    return warp


class _Reckon_by_time_run(object):
    _kwargs = ['park_time', 'park_test']
    run = None

    def __init__(self,
                 func: Optional[Callable]
                 ):
        self.func = func
        self.park_kwargs = {}
        self.args = tuple()
        self.kwargs = dict()
        self.obj = None

    def __get__(self,
                obj: Union[Any],
                klass: type(object) = None
                ):
        self.obj = obj

        def warp(*args, **kwargs):
            kwargs = self._park_kwargs(kwargs)
            self.args = args
            self.kwargs = kwargs
            return self._park()

        for flag, v in self.obj.flags.items():
            if v and flag in dir(self.func):
                eval(f'self._{flag}(func)', {'self': self.obj, 'func': self.func})
        return warp

    def _park(self) -> Union[Any]:
        func = self.func
        func = self.obj.load(ty='decorator', args=(func,))
        if self.run:
            if self.run and isinstance(self.run, (tuple, list)):
                if self.run[0] == 'park_time' and self.run[1]:
                    return self.park_time(func=func)
                elif self.run[0] == 'park_test':
                    return self.park_test(func=func)
        return func(*self.args, **self.kwargs)

    def park_time(self,
                  func: Optional[Callable]
                  ) -> Union[Any]:
        start_time = time.perf_counter()
        res = func(*self.args, **self.kwargs)
        end_time = time.perf_counter()

        info = {
            func.__name__: {
                'start_time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'speed_time': ('%.8f' % float(Decimal(end_time) - Decimal(start_time))).rstrip('0')
            }
        }
        self.obj.speed_info.update(info)
        return res

    def park_test(self,
                  func: Optional[Callable]
                  ) -> Union[Any]:
        base_time = 100
        info = {}
        if isinstance(self.run[1], dict):
            base_time = self.run[1].get('time', 100)
        res = None
        for _ in range(1, base_time + 1):
            sub_dict = {}
            start_time = time.perf_counter()
            try:
                res = func(*self.args, **self.kwargs)
            except Exception as e:
                sub_dict['error'] = str(e)
            finally:
                end_time = time.perf_counter()
                sub_dict['speed_time'] = ('%.8f' % float(Decimal(end_time) - Decimal(start_time))).rstrip('0')
                sub_dict['result'] = res
            info[_] = sub_dict
        self.obj.test_info.update({
            func.__name__: info
        })
        return res

    def _park_kwargs(self,
                     kwargs: dict
                     ) -> dict:
        new_kwargs = {}
        for key, val in kwargs.items():
            if key in self._kwargs:
                self.park_kwargs[key] = val
            else:
                new_kwargs[key] = val
        self.get_run()
        return new_kwargs

    def get_run(self) -> None:
        if 'park_test' in self.park_kwargs:
            self.run = ('park_test', self.park_kwargs['park_test'])
        elif 'park_time' in self.park_kwargs:
            self.run = ('park_time', self.park_kwargs['park_time'])
