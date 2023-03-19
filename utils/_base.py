import datetime
import time
from typing import (
    Union,
    Tuple,
    List,
    Any, Optional, Callable
)

from decimal import Decimal

from .paras import Paras
from .env import env, Io
from .api import reckon_by_time_run
from ..tools import _Context


class ReckonBasics(type):

    def __new__(
            mcs,
            name: str,
            bases: tuple,
            attrs: dict
    ):
        res = type.__new__(mcs, name, bases, attrs)
        if attrs['__qualname__'] == 'reckon_run':
            return res
        for attr in attrs:
            if attr == 'r_funcs':
                r_funcs = reckon_run.r_funcs + attrs[attr]
                setattr(reckon_run, attr, r_funcs)
                continue
            if attr not in dir(reckon_run):
                setattr(reckon_run, attr, attrs[attr])
        return None


class reckon_run(metaclass=ReckonBasics):
    r_funcs = ['park_time', 'park_test']
    run = None

    def __init__(
            self,
            func: Optional[Callable]
    ):
        self.func = func
        self.park_kwargs = {}
        self.args = tuple()
        self.kwargs = dict()
        self.obj = None

    def __get__(
            self,
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

    def _park(
            self
    ) -> Union[Any]:
        func = self.func
        func = self.obj.load(key='decorator', args=(func,))
        if self.run:
            if self.run and isinstance(self.run, (tuple, list)):
                f = eval(f'self.{self.run[0]}')
                return f(func=func)
        return func(*self.args, **self.kwargs)

    def park_time(
            self,
            func: Optional[Callable]
    ) -> Union[Any]:
        start_time = time.perf_counter()
        res = func(*self.args, **self.kwargs)
        end_time = time.perf_counter()

        def get_name(F):
            if hasattr(F, '__func__'):
                return get_name(F.__func__)
            return F

        name = get_name(func).__name__
        info = {
            name: {
                'start_time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'speed_time': ('%.8f' % float(Decimal(end_time) - Decimal(start_time))).rstrip('0')
            }
        }
        self.obj.speed_info.update(info)
        return res

    def park_test(
            self,
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

    def _park_kwargs(
            self,
            kwargs: dict
    ) -> dict:
        new_kwargs = {}
        for key, val in kwargs.items():
            if key in self.r_funcs:
                self.park_kwargs[key] = val
            else:
                new_kwargs[key] = val
        self.get_run()
        return new_kwargs

    def get_run(
            self
    ) -> None:
        for r_f in self.r_funcs:
            if r_f in self.park_kwargs:
                self.run = (r_f, self.park_kwargs[r_f])


def _inherit_parent(
        inherits: Union[str, List[str], Tuple[str]],
        attrs: dict
) -> Tuple[Tuple[Any], dict]:
    """
    用于查找父类并从父类继承属性，
    """
    bases = []
    if isinstance(inherits, str):
        parent = env[attrs.get('_inherit')]
        if not isinstance(parent, Basics):
            parent = parent.__class__
        bases = (parent,)
        if 'paras' in attrs and isinstance(attrs['paras'], Paras):
            attrs['paras'].inherit_update(parent.paras)
        else:
            paras = Paras()
            paras.inherit_update(parent.paras)
            attrs['paras'] = paras
    elif isinstance(inherits, (tuple, list)):
        for inherit in inherits:
            parent = env[inherit]
            if not isinstance(parent, Basics):
                parent = parent.__class__
            bases += [parent]
        p_paras = list(map(lambda x: x.paras, bases))
        if 'paras' in attrs and isinstance(attrs['paras'], Paras):
            attrs['paras'].inherit_update(p_paras)
        else:
            paras = Paras()
            paras.inherit_update(p_paras)
            attrs['paras'] = paras
        bases = tuple(bases)
    return bases, attrs


class Basics(type):
    """
    基础元类，对继承等操作进行补充
    """

    def __new__(
            mcs,
            name: str,
            bases: tuple,
            attrs: dict
    ):
        """
        重组定义的类，
        增加新的属性__new_attrs__
        添加默认属性 paras
        """
        mappings = list()
        _attrs = attrs.items()
        if attrs['__qualname__'] != 'ParkLY':
            if not attrs.get('_name') and not attrs.get('_inherit'):
                raise AttributeError("必须设置_name属性")
            if attrs.get('_name') and not attrs.get('_inherit'):
                if 'paras' not in attrs or ('paras' in attrs and not isinstance(attrs['paras'], Paras)):
                    attrs['paras'] = Paras()
            for key, val in _attrs:
                if not key.startswith('__') and not key.endswith('__'):
                    attrs[key] = reckon_by_time_run(val)
                    mappings.append(key)
        res = type.__new__(mcs, name, bases, attrs)
        # 存在_name _inherit 属性 ->（说明创造的类是继承父类的所有信息，并生成一个新类）
        if attrs.get('_name') and attrs.get('_inherit'):
            inherits = attrs.get('_inherit')
            assert isinstance(inherits, (str, tuple, list))
            _bases, attrs = _inherit_parent(inherits, attrs)
            res = type.__new__(mcs, name, _bases or bases, attrs)
            env(name=attrs.get('_name'), cl=res)
        # 此时仅创建一个类不继承任何属性
        elif attrs.get('_name'):
            env(name=attrs.get('_name'), cl=res)
        # 仅继承，为父类增加内容，覆盖env环境中的对应内容
        elif attrs.get('_inherit'):
            inherit = attrs.get('_inherit')
            assert isinstance(inherit, str)
            _bases, attrs = _inherit_parent(inherit, attrs)
            res = type.__new__(mcs, name, _bases or bases, attrs)
            env(name=inherit, cl=res, inherit=True)
        # 为每个构造的类增加 env属性 （self.env）
        setattr(res, 'env', env)
        setattr(res, 'io', Io())
        if hasattr(res, '__new_attrs__'):
            setattr(res, '__new_attrs__', res.__new_attrs__ + mappings)
        else:
            setattr(res, '__new_attrs__', mappings)
        return res
