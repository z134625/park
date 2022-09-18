
from typing import Any
from inspect import isroutine


__doc__ = """使用装饰器计算函数使用时间等信息
用法:
@timekeeping()
def func():
    pass    
-- timekeeping中支持传入msg = str, info = True 
    - msg 表示程序启动显示信息 默认为空
    - info 表示是否打印当前系统信息 默认为True
"""
__all__ = ("timer", )


def _timekeeping(msg: str = None,
                 thread: bool = False,
                 process: bool = False, asy: bool = False,
                 args: list = None,
                 *arg, **kwarg):
    """
    计时器装饰器
    支持装饰函数以及类方法
    msg： 表示打印开头的信息
    """
    from ..conf.os import base
    from ..conf.setting import (
        Time,
        Stamp,
        Command,
    )

    if isroutine(msg):
        return _timekeeping()(msg)

    def wrapper(func):
        def warp():
            if msg:
                print(msg)
            print(f"执行开始{Time}:")
            start: float = Stamp()
            result: Any = func(*arg, **kwarg)
            end: float = Stamp()
            time_ = end - start + 1 - 1
            print(f"{base(Command[0])}程序总耗时:{time_}")
            return result, time_
        return warp
    return wrapper


def _cache():
    pass


timer = _timekeeping

