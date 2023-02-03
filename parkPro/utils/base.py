import copy
import io
import os
import pickle
import re
import sys
from typing import (
    List,
    Union,
    Any,
    Set,
    Tuple
)
from types import (
    FunctionType,
    MethodType
)

from ._base import Basics
from .api import _Reckon_by_time_run
from .paras import Paras
from ..tools import (
    mkdir,
    warning,
    _Context
)
from .env import env


class ParkLY(object, metaclass=Basics):

    """
    为工具类中的基类，
    该类定义一些基础方法供使用
    也可自行增加元类， 创建。此操作将舍弃 基类中所有定义的方法
    """
    _name = 'ParkLY'
    _inherit = None
    root_func: List[str] = []
    paras: Paras = Paras()

    def __new__(cls, *args, **kwargs):
        """
        定义配置文件
        注册系统函数， 无权限不可调用
        """
        if cls.root_func:
            if cls.root_func == 'all':
                for func in cls.__new_attrs__:
                    cls._root_func(func)
            else:
                for func in cls.root_func:
                    cls._root_func(func)
        res = super().__new__(cls)
        return res

    def __init__(self, **kwargs):
        self.init(**kwargs)

    # def __call__(self, func=None, root: bool = False):
    #     """
    #     增加属性方法
    #     root 将对增加的方法施加管理员权限，
    #     当开启管理设置、 或自身方法调用时将不做限制
    #     """
    #     if func:
    #         setattr(self, func.__name__, MethodType(func, self))
    #
    #         def warp(*args, **kwargs):
    #             try:
    #                 return func(self, *args, **kwargs)
    #             except TypeError:
    #                 return func(*args, **kwargs)
    #
    #         return warp
    #
    #     def wrapper(func_s):
    #         if root:
    #             self.root_func += [func_s.__name__]
    #         setattr(self, func_s.__name__, MethodType(func_s, self))
    #
    #         def warps(*args, **kwargs):
    #             try:
    #                 return func_s(self, *args, **kwargs)
    #             except TypeError:
    #                 return func_s(*args, **kwargs)
    #
    #         return warps
    #
    #     return wrapper

    def init(self,
             **kwargs
             ) -> None:
        """
        类实例化时的初始化方法
        该方法将更新 环境变量中对应的对象
        未初始化的对对象， 环境变量中保存的未类
        """
        self.paras.update({'_attrs': self.paras._attrs})
        self.paras.update(kwargs)
        self.paras.update({'_obj': self._name}, is_obj=True)
        self.env._mapping.update({
            self._name: self
        })
        for f in dir(self):
            eval(f'self.{f}')

    def update(self,
               K: dict = None
               ) -> Union[Any]:
        if K is None:
            return self
        self.paras.update({
            '_attrs': K
        })
        return self

    @classmethod
    def _root_func(cls,
                   func: Union[Any, str]
                   ) -> None:
        if sys._getframe(1).f_code.co_name in ('__new__', '__setattr__'):
            name = func if isinstance(func, str) else func.__name__
            if name not in cls.paras.root_func:
                cls.paras.root_func.append(name)

    def __getattribute__(self,
                         item: str
                         ):
        """
        该对象不允许直接获取 以_开头的私有属性
        当开启root 权限时 即可 正常获取
        """
        call_name = sys._getframe(1).f_code.co_name
        if item.startswith('__') and item.endswith('__'):
            return super(ParkLY, self).__getattribute__(item)
        try:
            res = super(ParkLY, self).__getattribute__(item)
            if callable(res):
                if self.paras.root_func != self.root_func:
                    self.root_func = self.paras.root_func
                if item in self.paras.root_func and \
                        (
                                call_name not in self.__new_attrs__ and
                                call_name not in dir(ParkLY)
                        ):
                    if not self.paras._root and (hasattr(res, '__self__') and not isinstance(res.__self__, ParkLY)):
                        raise AttributeError('此方法(%s)为管理员方法，不可调用' % item)
                if 'reckon_by_time_run' in dir(res):
                    return _Reckon_by_time_run(res).__get__(self)
                return res
            return super(ParkLY, self).__getattribute__(item)
        except AttributeError:
            return self.__getitem__(item)

    def __getitem__(self,
                    item: str
                    ):
        if item.startswith('speed_info_'):
            func = re.match(r'^speed_info_([a-zA-Z_]\w+)', item)
            if func:
                if hasattr(self, func.group(1)):
                    eval('self.' + func.group(1) + '(park_time=True)')
            return super().__getattribute__('speed_info')
        elif self.paras._error:
            raise AttributeError('获取错误，没有该方法(%s)' % item)
        else:
            return False

    def __setattr__(self,
                    key: str,
                    value: Union[Any]
                    ):
        if key == 'root_func' and sys._getframe(1).f_code.co_name == 'wrapper':
            assert isinstance(value, (list, tuple))
            for val in value:
                self._root_func(val)
        if key not in set(dir(self)).difference(set(self.paras._attrs)):
            res = super(ParkLY, self).__setattr__(key, value)
            self.paras._attrs.update({key: value})
            return res
        return super(ParkLY, self).__setattr__(key, value)

    def save_log(self) -> None:
        for key in self._save_io:
            value = self.io[key].getvalue()
            save_path = os.path.join(self._save_path, key)
            mkdir(save_path)
            file = os.path.join(save_path, self._save_file +
                                (f'.{self._save_suffix.get(key)}' if self._save_suffix.get(
                                    key) else self._save_suffix.get(key, '')))
            mode = self._save_mode
            if isinstance(value, bytes):
                mode = self._save_mode + 'b'
            with open(file, mode, encoding=self._save_encoding if 'b' not in mode else None) as f:
                f.write(value)

    def sudo(self,
             gl: bool = False
             ) -> Any:
        """
        开启root权限
        """
        return self.with_root(gl=gl)

    def with_root(self,
                  gl: bool = False
                  ) -> Any:
        """
        生成带root权限的对象
        obj表示该类的实例
        """
        return self.with_paras(_root=True, gl=gl)

    def with_context(self,
                     context: dict = None,
                     gl: bool = False
                     ) -> Any:
        """
        携带上下文 新上下文的对象 默认为 字典形式
        :param context: 增加上下文的内容
        :param gl:  是否全局设置属性， 即修改自身， 默认为否， 创造一个新对对象修改配置
        :return : 对象本身
        """
        return self.with_paras(context=context or {}, gl=gl)

    def with_paras(self,
                   gl: bool = False,
                   **kwargs
                   ) -> Any:
        """
        修改配置主方法， 此方法将生成一个 一摸一样的新对象， 本质基本不变
        :param gl: 是否全局设置属性， 即修改自身， 默认为否， 创造一个新对对象修改配置
        :param kwargs:  修改的配置的参数
        :return : 对象本身
        """
        if not gl:
            obj: ParkLY = copy.deepcopy(self)
            paras: Paras = copy.deepcopy(self.paras)
            env(name=obj._name + '_paras', cl=obj, warn=False)
            paras.update({'_obj': obj._name + '_temporary'})
            if sys._getframe(1).f_code.co_name not in ('with_context', 'with_root'):
                if '_root' in kwargs:
                    kwargs.pop('_root')
                if 'context' in kwargs:
                    kwargs.pop('context')
            dif_set: Set[str] = set(kwargs.keys()).difference(set(self.paras._allow_set))
            if dif_set.__len__() >= 1:
                msg = '没有' + '、'.join(dif_set) + '配置，不允许设置'
                warning(msg, warn=kwargs.get('_warn', False) or self.paras._warn)
            paras_dict: dict = {}
            for key in set(kwargs.keys()).difference(dif_set):
                paras_dict.update({
                    key: kwargs[key]
                })
            obj.paras = paras
            obj.paras.update(paras_dict)
            return obj
        else:
            self.paras.update(kwargs)
            return self

    @property
    def context(self) -> _Context:
        """
        直接获取该实例的上下文
        :return : 上下文context
        """
        return self.paras.context

    @property
    def flags(self) -> _Context:
        """
        直接获取该实例的上下文
        :return : 上下文context
        """
        return self.paras.flags

    def save(self,
             file: Union[str, io.FileIO, io.BytesIO] = None,
             data: Any = None
             ) -> Union[str, io.FileIO, io.BytesIO]:
        """
        :param file: 保持序列化数据位置， 不提供则不保存，
        :param data: 需要序列化的数据， 不提供则序列化加载的配置文件内容
        :return : 序列化后的数据
        """
        if not data:
            data: dict = self.paras._attrs
        pickle_data = pickle.dumps(data)
        if file:
            if isinstance(file, str):
                dirs = os.path.dirname(file)
                mkdir(dirs)
                f = open(file, 'wb')
                pickle.dump(data, f)
                f.close()
            elif isinstance(file, io.BytesIO):
                file.write(pickle_data)
            elif isinstance(file, io.FileIO):
                file.write(pickle_data)
        return file

    def load(self,
             ty: Union[int, None] = None,
             args: Union[Tuple[Tuple[Any], dict], None] = None
             ):
        if ty:
            name = f'_load_{ty}'
            if hasattr(self, name):
                res = eval(f'self.{name}(*args)', {'self': self, 'args': args})
                return res

    def _load_decorator(self,
                        func: Union[MethodType, FunctionType]
                        ) -> Union[MethodType, FunctionType]:
        flag_func = list(filter(lambda x: x.endswith('_flag'), dir(func)))
        flag_attrs = {}
        for f in flag_func:
            attrs = getattr(func, f)
            flag_attrs.update({
                f: attrs
            })
        for name in flag_func:
            warp = 'self._' + name
            func = eval(f'{warp}(func)', {'self': self, 'func': func})
            for k, v in flag_attrs.items():
                setattr(func, k, v)
        return func

    def _load_pickle(self,
                     path: str = None,
                     data: Any = None
                     ) -> Union[dict, Any]:
        """
        :param path: 保持序列化数据位置， 不提供则为 加载文件属性，
        :param data: 需要反序列化的数据， 不提供则为 加载文件属性
        :return : 反序列化后的数据
        """
        if data:
            pickle_data = pickle.loads(data)
            return pickle_data
        if path and os.path.exists(path) and os.path.isfile(path):
            f = open(path, 'rb')
            pickle_data = pickle.load(f)
            return pickle_data
        return self.paras._attrs

    def give(self,
             obj: Union[Any],
             content: dict = None
             ):
        """
        此方法用于将自身属性给予给出的参数
        不提供content 则将自身的 新增的属性赋给 obj对象
        content 必须为字典形式
        以 key 变量名， value 变量值 可以为方法， 也可以为值
        """
        if not content:
            if isinstance(obj, ParkLY):
                obj.paras.update({
                    '_attrs': self.paras._attrs
                })
                return obj
            return self
        else:
            assert isinstance(content, dict)
            for key, value in content.items():
                if callable(value):
                    setattr(obj, key, value)
                else:
                    setattr(obj, key, value)
            obj.paras._attrs.update(content)
            return self
