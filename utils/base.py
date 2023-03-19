import copy
import io
import os
import pickle
import re
import sys
from collections.abc import Iterable
from typing import (
    List,
    Union,
    Any,
    Set,
    Tuple,
    TextIO
)
from types import (
    FunctionType,
    MethodType
)

from ._base import Basics, reckon_run
from .paras import Paras
from ..tools import (
    mkdir,
    warning,
    _Context,
    listPath,
    args_tools
)
from .env import env
from ._type import _ParkLY


class ParkLY(_ParkLY, metaclass=Basics):
    """
    为工具类中的基类，
    该类定义一些基础方法供使用
    也可自行增加元类， 创建。此操作将舍弃 基类中所有定义的方法
    """
    _name = 'ParkLY'
    _inherit = None
    root_func: List[str] = []
    paras: Paras = Paras()
    _type = 'normal'
    _inherit_update = []

    def __new__(
            cls,
            *args,
            **kwargs
    ):
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

    def __init__(
            self,
            **kwargs
    ):
        self.init(**kwargs)

    def init(
            self,
            **kwargs
    ) -> None:
        """
        类实例化时的初始化方法
        该方法将更新 环境变量中对应的对象
        未初始化的对对象， 环境变量中保存的未类
        """
        self.paras.update({'ATTRS': self.paras.ATTRS})
        self.paras.update(kwargs)
        self.paras.update({'OBJ': self._name}, is_obj=True)
        self.env._mapping.update({
            self._name: self
        })
        for f in dir(self):
            eval(f'self.{f}')

    def update(
            self,
            K: dict = None
    ) -> _ParkLY:
        if K is None:
            return self
        self.paras.update({
            'ATTRS': K
        })
        return self

    @classmethod
    def _root_func(
            cls,
            func: Union[Any, str]
    ) -> None:
        if sys._getframe(1).f_code.co_name in ('__new__', '__setattr__'):
            name = func if isinstance(func, str) else func.__name__
            if name not in cls.paras.root_func:
                cls.paras.root_func.append(name)

    def __getattribute__(
            self,
            item: str
    ) -> Any:
        """
        该对象不允许直接获取 以_开头的私有属性
        当开启root 权限时 即可 正常获取
        """
        res = super(ParkLY, self).__getattribute__(item)
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
                    if not self.paras.ROOT and (hasattr(res, '__self__') and not isinstance(res.__self__, ParkLY)):
                        raise AttributeError('此方法(%s)为管理员方法，不可调用' % item)
                if 'reckon_by_time_run' in dir(res):
                    return reckon_run(res).__get__(self)
                return res
            return res
        except AttributeError:
            return self.__getitem__(item)

    def __getitem__(
            self,
            item: str
    ):
        if item.startswith('speed_info_'):
            func = re.match(r'^speed_info_([a-zA-Z_]\w+)', item)
            if func:
                if hasattr(self, func.group(1)):
                    eval('self.' + func.group(1) + '(park_time=True)')
            return super().__getattribute__('speed_info')
        elif self.paras.ERROR:
            raise AttributeError('获取错误，没有该方法(%s)' % item)
        else:
            return False

    def __setattr__(
            self,
            key: str,
            value: Union[Any]
    ):
        if key == 'root_func' and sys._getframe(1).f_code.co_name == 'wrapper':
            assert isinstance(value, (list, tuple))
            for val in value:
                self._root_func(val)
        if key not in set(dir(self)).difference(set(self.paras.ATTRS)):
            super(ParkLY, self).__setattr__(key, value)
            self.paras.ATTRS.update({key: value})
            return
        return super(ParkLY, self).__setattr__(key, value)

    def _get_type_func(
            self,
            ty: str,
            key: str,
            args: Union[Any, None] = None
    ) -> None:
        if ty:
            name = f'_{ty}_{key}'
            if hasattr(self, name):
                args = args_tools(args=args, self=self)
                res = eval(f'self.{name}(*args, **kwargs)',
                           {'self': self, 'args': args[0] or (), 'kwargs': args[1] or {}}
                           )
                return res

    def open(
            self,
            file: str,
            mode: str = 'r',
            encoding: Union[None, str] = 'utf-8',
            lines: bool = False,
            datas: Any = None,
            get_file: bool = False
    ) -> Union[TextIO, None, Any]:
        method = None
        write = False
        if mode in ['r', 'rb']:
            method = 'readlines' if lines else 'read'
        elif mode in ['w', 'wb']:
            write = True
            method = 'writelines' if lines else 'write'
        elif mode in ['ab', 'a']:
            if not datas:
                method = 'readlines' if lines else 'read'
            else:
                write = True
                method = 'writelines' if lines else 'write'
        if 'b' in mode:
            encoding = None
        if method:
            res = None
            f = open(file, mode, encoding=encoding)
            if get_file:
                return f
            try:
                func = eval(f'f.{method}', {'f': f})
                res = func() if not write else func(datas)
            except Exception as e:
                self.env.log.error(e)
            finally:
                f.close()
            return res

    def save(
            self,
            key: Union[str, None] = None,
            args: Union[Tuple[Any], None] = None
    ) -> None:
        if key:
            return self._get_type_func(ty='save', key=key, args=args)

    def _save_log(
            self,
            name
    ) -> None:
        self._save_file(key='log', name=name)

    def _save_file(
            self,
            key=None,
            name: str = 'park'
    ) -> None:
        keys = self.save_io
        if key:
            keys = [key]
        for key in keys:
            value = self.io[key].getvalue()
            save_path = os.path.join(self.SAVE_PATH, key)
            mkdir(save_path)
            file = os.path.join(save_path, name +
                                (f'.{self.SAVE_SUFFIX.get(key)}' if self.SAVE_SUFFIX.get(
                                    key) else self.SAVE_SUFFIX.get(key, '')))
            file = self.exists_rename(file)
            mode = self.SAVE_MODE
            if isinstance(value, bytes):
                mode = self.SAVE_MODE + 'b'
            self.open(file,
                      mode=mode,
                      encoding=self.SAVE_ENCODING if 'b' not in mode else None,
                      datas=value
                      )

    def get(
            self,
            content: dict
    ) -> _ParkLY:
        assert isinstance(content, dict)
        self.update(content)
        return self

    def sudo(
            self,
            gl: bool = False
    ) -> _ParkLY:
        """
        开启root权限
        """
        return self.with_root(gl=gl)

    def with_root(
            self,
            gl: bool = False
    ) -> _ParkLY:
        """
        生成带root权限的对象
        obj表示该类的实例
        """
        return self.with_paras(ROOT=True, gl=gl)

    def with_context(
            self,
            context: dict = None,
            gl: bool = False
    ) -> _ParkLY:
        """
        携带上下文 新上下文的对象 默认为 字典形式
        :param context: 增加上下文的内容
        :param gl:  是否全局设置属性， 即修改自身， 默认为否， 创造一个新对对象修改配置
        :return : 对象本身
        """
        return self.with_paras(context=context or {}, gl=gl)

    def with_paras(
            self,
            gl: bool = False,
            **kwargs
    ) -> _ParkLY:
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
                if 'ROOT' in kwargs:
                    kwargs.pop('ROOT')
                if 'context' in kwargs:
                    kwargs.pop('context')
            dif_set: Set[str] = set(kwargs.keys()).difference(set(self.paras.ALLOW_SET))
            if dif_set.__len__() >= 1:
                msg = '没有' + '、'.join(dif_set) + '配置，不允许设置'
                warning(msg, warn=kwargs.get('_warn', False) or self.paras.WARN)
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
    def context(
            self
    ) -> _Context:
        """
        直接获取该实例的上下文
        :return : 上下文context
        """
        return self.paras.context

    @property
    def flags(
            self
    ) -> _Context:
        """
        直接获取该实例的上下文
        :return : 上下文context
        """
        return self.paras.flags

    def _save_pickle(
            self,
            file: Union[str, io.FileIO, io.BytesIO] = None,
            data: Any = None
    ) -> Union[str, io.FileIO, io.BytesIO]:
        """
        :param file: 保持序列化数据位置， 不提供则不保存，
        :param data: 需要序列化的数据， 不提供则序列化加载的配置文件内容
        :return : 序列化后的数据
        """
        if not data:
            data: dict = self.paras.ATTRS
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

    def load(
            self,
            key: Union[str, None] = None,
            args: Union[Tuple[Tuple[Any], dict], dict, List, Tuple, None] = None
    ):
        if key:
            return self._get_type_func(ty='load', key=key, args=args)

    def _load_decorator(
            self,
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

    def _load_pickle(
            self,
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
        return self.paras.ATTRS

    def exists_rename(
            self,
            path: str,
            paths: List[str] = None,
            clear: bool = False,
            dif: bool = False) -> str:
        if not clear:
            if os.path.isdir(path):
                if path.endswith('/'):
                    path = path[:-1]
                names = listPath(path=os.path.dirname(path), splicing=False, list=True)
                return os.path.join(os.path.dirname(path), self.generate_name(name=os.path.basename(path),
                                                                              names=names, dif=dif))
            if os.path.isfile(path):
                names = listPath(path=os.path.dirname(path), splicing=False, list=True)
                return os.path.join(os.path.dirname(path), self.generate_name(name=os.path.basename(path),
                                                                              names=names, mode=1, dif=dif))
            else:
                names = []
                if paths:
                    names = paths
                return self.generate_name(name=path, names=names, dif=dif)
        else:
            name, suffix = os.path.splitext(path)
            pattern = re.compile(r'(.*) \([0-9]+\)')
            res = re.search(pattern=pattern, string=name)
            if res:
                name_head = res.group(1)
                return name_head + suffix
            else:
                return path

    def generate_name(
            self,
            name: str,
            names: Iterable,
            mode: int = 0,
            dif: bool = False,
            suffix: bool = '',
    ) -> str:
        if mode == 1:
            name, suffix = os.path.splitext(name)
            names = list(
                map(lambda x: os.path.splitext(x)[0], filter(lambda x: os.path.splitext(x)[1] == suffix, names)))
        if name in names:
            start = ' (1)'
            pattern_number = re.compile(r'.* \((\d+)\)')
            pattern_letter = re.compile(r'.* \(([A-Z]+)\)')
            pattern = pattern_number
            if dif:
                start = ' (A)'
                pattern = pattern_letter
            number = re.match(pattern=pattern, string=name)
            if number:
                number = number.group(1)
                if not dif:
                    new_name = re.sub(r'\(\d+\)$', '(%d)' % (int(number) + 1), name)
                else:
                    if not number.endswith('Z'):
                        new_name = re.sub(r'\([A-Z]+\)$', '(%s)' % (number[:-1] + chr(ord(number[-1]) + 1)), name)
                    else:
                        new_name = re.sub(r'\([A-Z]+\)$', '(%s)' % (number + 'A'), name)
            else:
                new_name = name + start
            if new_name in names:
                return self.generate_name(new_name, names, mode=0, dif=dif, suffix=suffix)
            return new_name + suffix
        return name + suffix
