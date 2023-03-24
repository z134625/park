from types import (
    MethodType,
    FunctionType,
    LambdaType,
    ModuleType
)
from typing import (
    Union,
    Tuple,
    List,
    Callable,
    Any,
    Optional,
    Dict
)

MONITOR_VAR = 0
MONITOR_FUNC = 1
MONITOR_ORDER_AFTER = 0
MONITOR_ORDER_BEFORE = 1


def command(
        keyword: Union[str, Tuple[str], List[str], dict],
        name: str,
        unique: bool = False,
        priority: int = -1
) -> Callable[[Any], Any]:
    """
    命令窗口装饰器，
    使用该装饰器必须继承自 Command
    xx.py
    ....
    main()

    python xx.py -h 1000 --host=1000
    """

    def warp(
            func: Union[MethodType, FunctionType]
    ) -> Union[Any]:
        setattr(func, 'command_flag', {
            'name': name,
            'keyword': keyword,
            'unique': unique,
            'priority': priority,
        })
        return func

    return warp


def monitor(
        fields: Union[str, Tuple[str], List[str], Dict[Any, str]],
        args: Union[Tuple[Tuple, dict], Tuple[Any], LambdaType, None, Any] = None,
        before_args: Union[Tuple[Tuple, dict], Tuple[Any], LambdaType, None, Any] = None,
        after_args: Union[Tuple[Tuple, dict], Tuple[Any], LambdaType, None, Any] = None,
        ty: int = MONITOR_FUNC,
        order: int = MONITOR_ORDER_AFTER
) -> Callable[[Any], Any]:
    """
    监控装饰器，
    使用该装饰器必须继承自 monitor
    可对变量监控，方法监控
    """

    def warp(func):
        kwargs = {
            ty: {
                'fields': fields,
                'args': args or (),
                'before_args': before_args or (),
                'after_args': after_args or (),
                'order': order,
            }
        }
        data = {}
        if hasattr(func, 'monitor_flag'):
            data = getattr(func, 'monitor_flag')
            data.update(kwargs)
        else:
            data.update(kwargs)
        setattr(func, 'monitor_flag', data)
        return func

    return warp


def reckon_by_time_run(
        func: Optional[Callable]
) -> Optional[Callable]:
    """
    基础装饰器，所有继承自ParkLY的方法
    方法中支持传参 park_time park_test
    用于测试方法性能
    """
    if callable(func):
        return setattr(func, 'reckon_by_time_run', True) or func
    return func


apis = locals()


def api_register(api_func):
    if callable(api_func):
        apis[api_func.__name__] = api_func
        return
    if isinstance(api_func, ModuleType):
        for f in dir(api_func):
            if callable(eval(f'api_func.{f}')) and not f.startswith('__') and not f.endswith('__'):
                apis[f] = eval(f'api_func.{f}')
