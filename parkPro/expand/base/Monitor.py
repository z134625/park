from typing import (
    Callable,
    Tuple,
    Any,
    Dict,
    Union,
    List
)
from types import (
    FunctionType,
    MethodType,
    WrapperDescriptorType,
    MethodWrapperType
)

from .paras import MonitorParas
from ...utils.base import ParkLY


class Monitor(ParkLY):
    """
    监控主要类
    使用方式
    """
    _name = 'monitor'
    paras = MonitorParas()

    def _monitor_flag(self,
                      res: Union[FunctionType, MethodType]
                      ) -> Callable[[Tuple[Any], Dict[str, Any]], Any]:
        if hasattr(res, 'monitor_flag'):
            fields = res.monitor_flag['fields']
            args = res.monitor_flag['args']
            order = res.monitor_flag['order']
            if callable(args):
                args = args(self)
                if isinstance(args, (tuple, list)):
                    args = (args, {})
                elif isinstance(args, dict):
                    args = ((), args)
                else:
                    args = ((args,), {})
            if res.monitor_flag['type']:
                return self._monitoring(func=res, fields=fields,
                                        arg=args, order=order)
            return self._monitoringV(func=res, fields=fields,
                                     arg=args, order=order)
        return res

    def _monitoring(self,
                    func: Union[FunctionType, MethodType, WrapperDescriptorType, MethodWrapperType],
                    fields: Union[str, List[str], Tuple[str]],
                    arg: Union[Tuple[tuple, dict], Tuple[Any]],
                    order: int
                    ) -> Union[Any]:

        def monitoring_warps(*args, **kwargs):
            root = self.paras._root
            self.paras.update({'_root': True})
            if order == 1:
                self._monitoring_go(res=False, fields=fields, func=func, arg=arg)
            res = func(*args, **kwargs)
            if order == 0:
                self._monitoring_go(res=res, fields=fields, func=func, arg=arg)
            self.paras.update({'_root': root})
            self.context.funcName = None
            return res

        return monitoring_warps

    def _monitoring_go(self,
                       res: Union[Any],
                       fields: Union[str, List[str], Tuple[str]],
                       func: Union[FunctionType, MethodType, WrapperDescriptorType, MethodWrapperType],
                       arg: Union[Tuple[tuple, dict], Tuple[Any]]
                       ) -> None:
        self.context.update({'return_result': res})
        if isinstance(fields, str):
            monit_func = getattr(self, fields)
            self.context.funcName = func.__name__
            monit_func(*arg[0], **arg[1])
        elif isinstance(fields, (list, tuple, set)):
            for f in fields:
                monit_func = getattr(self, f)
                self.context.funcName = func.__name__
                monit_func(*arg[0], **arg[1])
        self.context.update({'return_result': res})

    def _monitoringV(self,
                     func: Union[FunctionType, MethodType, WrapperDescriptorType, MethodWrapperType],
                     fields: Union[str, List[str], Tuple[str]],
                     arg: Union[Tuple[tuple, dict], Tuple[Any]],
                     order: int
                     ) -> Callable[[Tuple[Any], Dict[str, Any]], Any]:
        self.context.monitor_fields.add(fields)
        self.context.monitor_func[fields] = func.__name__
        self.context.monitor_func_args[fields] = (arg, order)

        def monitoringV_warps(*args, **kwargs):
            res = func(*args, **kwargs)
            return res

        return monitoringV_warps

    def __setattr__(self,
                    key: str,
                    value: Union[Any]
                    ):
        order = -1
        func = None
        args = None
        if key in self.context.monitor_fields:
            func = self.context.monitor_func[key]
            func = eval(f'self.{func}')
            args, order = self.context.monitor_func_args[key]
        if order == 1:
            func(*args[0], **args[1])
        res = super(Monitor, self).__setattr__(key=key, value=value)
        if order == 0:
            func(*args[0], **args[1])
        return res
