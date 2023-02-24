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
from ...utils import api
from ...utils.base import ParkLY
from ...tools import args_tools


class Monitor(ParkLY):
    """
    监控主要类
    使用方式
    """
    _name = 'monitor'
    paras = MonitorParas()

    def _monitor_flag(
            self,
            res: Union[FunctionType, MethodType]
    ) -> Callable[[Tuple[Any], Dict[str, Any]], Any]:
        if hasattr(res, 'monitor_flag'):
            data = []
            if 0 in res.monitor_flag:
                data.append((0, res.monitor_flag[0]))
            if 1 in res.monitor_flag:
                data.append((1, res.monitor_flag[1]))
            func = res
            for i, item in data:
                fields = item['fields']
                order = item['order']
                if isinstance(fields, dict):
                    field = list(fields.items())
                    before = list(map(lambda x: x[1], filter(lambda x: x[0] == api.MONITOR_ORDER_BEFORE, field)))
                    after = list(map(lambda x: x[1], filter(lambda x: x[0] == api.MONITOR_ORDER_AFTER, field)))
                else:
                    if order == 1:
                        before = fields
                        after = []
                    else:
                        before = []
                        after = fields

                args = item['args']
                before_args = item['before_args']
                after_args = item['after_args']
                args = args_tools(args=args,
                                  self=self
                                  )

                before_args = args_tools(args=before_args,
                                         self=self
                                         )
                before_args = before_args if before_args != ((), {}) else args

                after_args = args_tools(args=after_args,
                                        self=self
                                        )
                after_args = after_args if after_args != ((), {}) else args
                if i:
                    func = self._monitoring(func=func,
                                            before=before,
                                            after=after,
                                            before_args=before_args,
                                            after_args=after_args,
                                            )
                else:
                    func = self._monitoringV(func=func,
                                             before=before,
                                             after=after,
                                             before_args=before_args,
                                             after_args=after_args,
                                             )
            return func
        return res

    def _monitoring(
            self,
            func: Union[FunctionType, MethodType, WrapperDescriptorType, MethodWrapperType],
            before: Union[str, List[str], Tuple[str], Dict[Any, str]],
            after: Union[str, List[str], Tuple[str], Dict[Any, str]],
            before_args: Union[Tuple[tuple, dict], Tuple[Any]],
            after_args: Union[Tuple[tuple, dict], Tuple[Any]],
    ) -> Union[Any]:

        def monitoring_warps(
                *args,
                **kwargs
        ):
            root = self.paras._root
            self.paras.update({'_root': True})
            self._monitoring_go(res=False, fields=before, func=func, arg=before_args)
            res = func(*args, **kwargs)
            self._monitoring_go(res=res, fields=after, func=func, arg=after_args)
            self.paras.update({'_root': root})
            self.context.funcName = None
            return res

        setattr(monitoring_warps, '__func__', func)
        return monitoring_warps

    def _monitoring_go(
            self,
            res: Union[Any],
            fields: Union[str, List[str], Tuple[str]],
            func: Union[FunctionType, MethodType, WrapperDescriptorType, MethodWrapperType],
            arg: Union[Tuple[tuple, dict], Tuple[Any]],
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
        self.context.update({'return_result': False})

    def _monitoringV(
            self,
            func: Union[FunctionType, MethodType, WrapperDescriptorType, MethodWrapperType],
            before: Union[str, List[str], Tuple[str]],
            after: Union[str, List[str], Tuple[str]],
            before_args: Union[Tuple[tuple, dict], Tuple[Any]],
            after_args: Union[Tuple[tuple, dict], Tuple[Any]],
    ) -> Callable[[Tuple[Any], Dict[str, Any]], Any]:
        before = [before] if isinstance(before, str) else before
        after = [after] if isinstance(after, str) else after
        for field1 in before:
            self.context.monitor_before_fields.add(field1)
            self.context.monitor_before_func[field1] = func.__name__
            self.context.monitor_func_before_args[field1] = before_args
        for field2 in after:
            self.context.monitor_after_fields.add(field2)
            self.context.monitor_after_func[field2] = func.__name__
            self.context.monitor_func_after_args[field2] = after_args

        def monitoringV_warps(
                *args,
                **kwargs
        ):
            res = func(*args, **kwargs)
            return res

        setattr(monitoringV_warps, '__func__', func)
        return monitoringV_warps

    def _monitoringV_go(
            self,
            key: str,
            ty: int,
    ) -> None:
        func = False
        args = ((), {})
        if ty == api.MONITOR_ORDER_BEFORE and key in self.context.monitor_before_fields:
            func = self.context.monitor_before_func[key]
            args = self.context.monitor_func_before_args[key]
        elif ty == api.MONITOR_ORDER_AFTER and key in self.context.monitor_after_fields:
            func = self.context.monitor_after_func[key]
            args = self.context.monitor_func_after_args[key]
        if func:
            func = eval(f'self.{func}')
            func(*args[0], **args[1])

    def __setattr__(
            self,
            key: str,
            value: Union[Any]
    ):
        self._monitoringV_go(key, ty=api.MONITOR_ORDER_BEFORE)
        res = super(Monitor, self).__setattr__(key=key, value=value)
        self._monitoringV_go(key, ty=api.MONITOR_ORDER_AFTER)
        return res
