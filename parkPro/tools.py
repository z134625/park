import json
import os
import re
import shutil
import sys
import copy
import pickle

import warnings
import configparser
from typing import Union, List, Any, Tuple, Set
from types import MethodType
from . import LISTFILE


def warning(msg: str, warn: bool = True,
            types: warnings = RuntimeWarning,
            stacklevel: int = 2) -> None:
    """
    警告方法，
    """
    if warn:
        warnings.warn(msg, types, stacklevel=stacklevel)
    return


def mkdir(path: str, exist: bool = True) -> bool:
    """
    创建文件夹
    """
    dir_: str = path
    try:
        os.mkdir(dir_)
    except FileExistsError:
        return False
    except FileNotFoundError:
        os.makedirs(dir_, exist)
    finally:
        return True


def remove(path: str, warn=True) -> bool:
    """删除文件"""
    try:
        os.remove(path)
        return True
    except PermissionError:
        shutil.rmtree(path)
        return True
    except FileNotFoundError:
        warning(f"该文件或文件夹({path})不存在或已删除", warn=warn)
        return False


def listPath(path: str, mode: int = LISTFILE, **kwargs) -> Union[list, map, filter]:
    """
    列出路径下的所有文件
    :param path: 路径
    :param kwargs: 支持使用where进行条件筛选， where 传入参数应为一种函数或者方法，需要的则应返回True， 不需要的返回False
    :return : 一组文件名
    """
    doc: bool = False
    dir_: bool = False
    if mode == 0:
        doc: bool = True
    elif mode == 1:
        dir_: bool = True
    like: str = kwargs.get("like", None)
    list_: bool = kwargs.get("list", True)
    splicing: bool = kwargs.get("splicing", False)
    files: List[str] = list(filter(lambda x: not x.startswith('.'), os.listdir(path)))
    if doc:
        files: filter = filter(lambda x: os.path.isfile(os.path.join(path, x)), files)
    if dir_:
        files: filter = filter(lambda x: os.path.isdir(os.path.join(path, x)) if not x.startswith('.') else False,
                               files)
    if like:
        files: filter = filter(lambda x: like in x, files)
    if splicing:
        files: map = map(lambda x: os.path.join(path, x), files)
    if list_:
        files: List[str] = list(files)
    return files


def readPy(file: str) -> dict:
    """
    file 为 字符串
    将py格式的字符串中的变量生成字典形式返回
    """
    exec(file)
    return locals()


def setAttrs(obj: Any, self: bool = False, cover: bool = True, warn: bool = True, **kwargs) -> Any:
    """
    对传入的obj 对象设置属性， 必须保证该对象有paras 属性，并且paras为Paras
    对于有paras 属性的 对象， 可在paras 设置属性 _cover 以及 _warn 来限制是否弹出警告 是否覆盖属性内容
    对于非paras 的对象 可在添加参数cover warn 默认都为True 设置的属性 增加函数参数即可
    即： setAttrs(obj, _cover=True, _warn=False
    对应的 这将对obj 对象设置 _cover _warn 两个参数
    设置的属性为 _set_dict 中的字典数据  调用方式
    obj.key = value
    self 参数在复制一个对象时， 会重复设置属性此时 为True避免重复警告  默认为False
    """
    if hasattr(obj, 'paras') and isinstance(obj.paras, Paras):
        cover: bool = True
        warn: bool = True
        for key, value in obj.paras._set_list:
            root = obj.paras._root
            if not root:
                obj.paras._root = True
            has: bool = key in dir(obj)
            if not root:
                obj.paras._root = False
            if not has:
                setattr(obj, key, value)
            else:
                warning("当前设置重复的属性(%s)，将覆盖该属性" % key,
                        warn=(warn and obj.paras._warn) and (cover and obj.paras._cover) and not self)
                if cover and obj.paras._cover:
                    setattr(obj, key, value)
            if obj.paras._root:
                d: dict = {
                    key: eval(f'obj.{key}')
                }
            else:
                obj.paras._root = True
                d: dict = {
                    key: eval(f'obj.{key}')
                }
                obj.paras._root = False
            obj.paras._attrs.update(d)
        obj.paras._set_list.clear()
    elif kwargs:
        for key, value in kwargs.items():
            warning("当前设置重复的属性(%s)，将覆盖该属性" % key, warn=warn and cover)
            if cover:
                setattr(obj, key, value)
    return obj


_ = lambda x: x


class RegisterEnv:

    def __init__(self):
        self._mapping: dict = {}

    def __call__(self, name, cl):
        self._register(name=name, cl=cl)

    def _register(self, name, cl):
        self._mapping.update(
            {name: cl}
        )

    def __setattr__(self, key, value):
        if key == '_mapping' and sys._getframe(1).f_code.co_name != '__init__':
            raise AttributeError("不允许设置该属性%s" % key)
        return super(RegisterEnv, self).__setattr__(key, value)

    def __getitem__(self, item):
        if item in self._mapping:
            return self._mapping[item]
        raise KeyError('没有注册该配置(%s)' % item)

    def load(self):
        mapping = {}
        for key in self._mapping:
            if isinstance(self._mapping[key], Basics):
                mapping.update({
                    key: self._mapping[key]()
                })

    def clear(self):
        return self._mapping.clear()


Register = RegisterEnv()


class Paras:
    """
    配置基础类
    含有参数
    _allow 默认允许 设置属性
    _allow_set 表示允许随时修改属性 设置属性
    """
    # 配置方法权限
    _allow: bool = False
    # 允许设置修改的属性
    _allow_set: list = []
    # 配置中的设置， 不允许修改的列表
    ban: List[str] = []
    # 默认配置中， 不允许修改的列表
    _ban: List[str] = ['_set_list', '_obj']

    def __init__(self, allow: bool = True, **kwargs):
        """
        默认初始化时允许设置属性
        """
        # 获取配置字典
        set_dict = {**self._init(), **self.init()}
        self._set_paras(allow=allow, kwargs=set_dict)
        for key in set(self.ban + self._ban):
            if key in self._allow_set:
                self._allow_set.remove(key)

    @staticmethod
    def init() -> dict:
        # 增加的配置
        return {}

    @staticmethod
    def _init() -> dict:
        # 系统基础配置
        # 对象的root权限
        _root: bool = False
        # 一些警告，默认开启
        _warn: bool = True
        # 设置属性时，是否覆盖 默认开启
        _cover: bool = True
        # 当对象获取属性时，是否报错 默认开启
        _error: bool = True
        # 设置属性的列表， 在设置成功后将删除
        _set_list: List[str] = []
        # 设置成功的属性和值
        _attrs: dict = {}
        # 配置上下文
        context: dict = {}
        # 管理员权限方法
        root_func: List[str] = []
        # 对增加方法 授权使用管理员方法
        grant: Set[str] = set()
        _obj: str = None
        return locals()

    def _set_paras(self, allow: bool = True, kwargs: dict = None) -> None:
        """
        修改属性方法，
        """
        if kwargs is None:
            kwargs = {}
        self._allow = allow
        try:
            if sys._getframe(1).f_code.co_name == 'update':
                pop_keys = []
                for key in kwargs.keys():
                    if key not in self._allow_set:
                        pop_keys.append(key)
                for key in pop_keys:
                    if key != '_obj':
                        kwargs.pop(key)
            if sys._getframe(1).f_code.co_name in ('update', '__init__'):
                if '_attrs' in kwargs:
                    attrs = kwargs.get('_attrs', {})
                    if isinstance(attrs, (list, tuple)):
                        kwargs.update({
                            '_set_list': attrs
                        })
                    elif isinstance(attrs, dict):
                        kwargs.update({
                            '_set_list': list(attrs.items())
                        })
                    sys_attrs = self._attrs if self._attrs else {}
                    kwargs['_attrs'] = {**sys_attrs}
                pattern = re.compile(r'^attrs_([a-zA-Z_]+)')
                _set_list = kwargs.get('_set_list', [])
                for key in kwargs.keys():
                    res = re.search(pattern, key)
                    if res:
                        attr = res.group(1)
                        _set_list.append((attr, kwargs[key]))
                kwargs.update({
                    '_set_list': _set_list
                })
                setAttrs(self, warn=False, **kwargs)
                for key in kwargs.keys():
                    if key not in self._allow_set:
                        self._allow_set.append(key)
                    self._allow_set = list(set(self._allow_set))
                self._update()
        except Exception as e:
            warning(f"属性设置失败 原因：{e}", warn=True)
            raise e
        finally:
            self._allow = False

    def _get_cls_dir(self, obj: Any = None):
        """
        获取self对象包含的 方法
        """
        if obj:
            return dir(obj)
        return self._allow_set

    def __setattr__(self, key, value):
        """
        该类不允许设置除 _allow 权限的属性
        若需要增加设置的属性
        则需要继承下 修改_allow_set 列表
        """
        if key == '_allow' and sys._getframe(1).f_code.co_name != '_set_paras' or \
                key == '_root' and sys._getframe(1).f_code.co_name != 'setAttrs':
            raise AttributeError('该类不允许设置属性(%s)' % key)
        elif key not in ('_allow', '_root'):
            if key not in self._allow_set and not self._allow:
                raise AttributeError('该类不允许设置属性(%s)' % key)
        return super(Paras, self).__setattr__(key, value)

    def update(self, kwargs: dict) -> Any:
        self._set_paras(allow=True, kwargs=kwargs)
        return self

    def __getattr__(self, item):
        if item in self._get_cls_dir() or item.startswith('__') and item.endswith('__'):
            return super(Paras, self).__getattr__(item)
        else:
            return False

    def _update(self):
        if self._obj:
            obj = Register[self._obj]
            return setAttrs(obj=obj)
        return None


class Basics(type):

    def __new__(mcs, name, bases, attrs):
        mappings = set()
        if attrs['__qualname__'] != 'ParkLY':
            if not attrs.get('_name') and not attrs.get('_inherit'):
                raise AttributeError("必须设置_name属性")
            if attrs.get('_name') and not attrs.get('_inherit'):
                if 'paras' not in attrs or ('paras' in attrs and not isinstance(attrs['paras'], Paras)):
                    attrs['paras'] = Paras()
            if attrs.get('_inherit'):
                if 'paras' in attrs and not isinstance(attrs['paras'], Paras):
                    attrs.pop('paras')
            for key, val in attrs.items():
                if key not in ['__module__', '__qualname__']:
                    mappings.add(key)
        attrs['__new_attrs__'] = mappings
        res = type.__new__(mcs, name, bases, attrs)
        if attrs.get('_name') and attrs.get('_inherit'):
            parent = Register[attrs.get('_inherit')]
            if not isinstance(parent, Basics):
                parent = parent.__class__
            bases = (parent,)
            res = type.__new__(mcs, name, bases, attrs)
            Register(name=attrs.get('_name'), cl=res)
        elif attrs.get('_name'):
            Register(name=attrs.get('_name'), cl=res)
        elif attrs.get('_inherit'):
            parent = Register[attrs.get('_inherit')]
            if not isinstance(parent, Basics):
                parent = parent.__class__
            bases = (parent,)
            res = type.__new__(mcs, name, bases, attrs)
            Register(name=attrs.get('_inherit'), cl=res)
        setattr(res, 'env', Register)
        return res


class ParkLY(object, metaclass=Basics):
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
        return super().__new__(cls)

    def __init__(self, **kwargs):
        self.init(**kwargs)

    def __call__(self, func=None, root: bool = False):
        """
        增加属性方法
        """
        if func:
            setattr(self, func.__name__, MethodType(func, self))

            def warp(*args, **kwargs):
                try:
                    return func(self, *args, **kwargs)
                except TypeError:
                    return func(*args, **kwargs)

            return warp

        def wrapper(func_s):
            if root:
                self.root_func += [func_s.__name__]
            setattr(self, func_s.__name__, MethodType(func_s, self))

            def warps(*args, **kwargs):
                try:
                    return func_s(self, *args, **kwargs)
                except TypeError:
                    return func_s(*args, **kwargs)

            return warps

        return wrapper

    def init(self, **kwargs):
        self.paras.update(kwargs)
        self.env._mapping.update({
            self._name: self
        })
        self.paras.update({'_obj': self._name})

    @classmethod
    def _root_func(cls, func: Union[Any, str]):
        if sys._getframe(1).f_code.co_name in ('__new__', '__setattr__'):
            name = func if isinstance(func, str) else func.__name__
            if name not in cls.paras.root_func:
                cls.paras.root_func.append(name)

    def __getattribute__(self, item):
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
                        (call_name not in self.paras.grant and
                         call_name not in self.__new_attrs__ and
                         call_name not in dir(ParkLY)):
                    if not self.paras._root:
                        raise AttributeError('此方法(%s)为管理员方法，不可调用' % item)
                return res
            if item.startswith("_") and not self.paras._root and \
                    (call_name not in self.paras.grant and
                     call_name not in self.__new_attrs__ and
                     call_name not in (dir(self))):
                raise KeyError("不允许获取私有属性(%s)" % item)
            return super(ParkLY, self).__getattribute__(item)
        except AttributeError as e:
            if self.paras._error:
                raise e
            else:
                return None

    def __setattr__(self, key, value):
        if key == 'root_func' and sys._getframe(1).f_code.co_name == 'wrapper':
            assert isinstance(value, (list, tuple))
            for val in value:
                self._root_func(val)
        if key not in set(dir(self)).difference(set(self.paras._attrs)):
            super(ParkLY, self).__setattr__(key, value)
            self.paras._attrs.update({key: value})
        if key == 'paras' and sys._getframe(1).f_code.co_name == 'with_paras':
            return super(ParkLY, self).__setattr__(key, value)

    def grant(self, func):
        self.paras.grant.add(func.__name__)
        return func

    def sudo(self, gl: bool = False) -> Any:
        """
        开启root权限
        """
        return self.with_root(gl=gl)

    def with_root(self, gl: bool = False) -> Any:
        """
        生成带root权限的对象
        obj表示该类的实例
        """
        return self.with_paras(_root=True, gl=gl)

    def with_context(self, context: dict = None, gl: bool = False) -> Any:
        """
        携带上下文 新上下文的对象 默认为 字典形式
        :param context: 增加上下文的内容
        :param gl:  是否全局设置属性， 即修改自身， 默认为否， 创造一个新对对象修改配置
        :return : 对象本身
        """
        return self.with_paras(context=context or {}, gl=gl)

    def with_paras(self, gl: bool = False, **kwargs) -> Any:
        """
        修改配置主方法， 此方法将生成一个 一摸一样的新对象， 本质基本不变
        :param gl: 是否全局设置属性， 即修改自身， 默认为否， 创造一个新对对象修改配置
        :param kwargs:  修改的配置的参数
        :return : 对象本身
        """
        if not gl:
            obj: ParkLY = copy.deepcopy(self)
            paras: Paras = copy.deepcopy(self.paras)
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
            paras.update(paras_dict)
            obj.paras = paras
            obj.paras.update({'_attrs': obj.paras._attrs})
            return obj
        else:
            self.paras.update(kwargs)
            return self

    @property
    def context(self) -> dict:
        """
        直接获取该实例的上下文
        :return : 上下文context
        """
        return self.paras.context

    def save(self, path: str = None, data: Any = None) -> bytes:
        """
        :param path: 保持序列化数据位置， 不提供则不保存，
        :param data: 需要序列化的数据， 不提供则序列化加载的配置文件内容
        :return : 序列化后的数据
        """
        if not data:
            data: dict = self.paras._attrs
        pickle_data = pickle.dumps(data)
        if path:
            dirs = os.path.dirname(path)
            mkdir(dirs)
            f = open(path, 'wb')
            pickle.dump(data, f)
            f.close()
        return pickle_data

    def load(self, path: str = None, data: Any = None) -> Union[dict, Any]:
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

    def give(self, obj, content=None):
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
                    func = value.__func__ if hasattr(value, '__func__') else value
                    setattr(obj, key, MethodType(func, obj))
                else:
                    setattr(obj, key, value)
            obj.paras._attrs.update(content)
            return self


class SettingParas(Paras):
    """
    配置文件类
    默认包含
    _root  超级权限， 目前仅提供 查询 _{item} 的内置属性
    _warn  是否弹出警告 信息
    _cover 设置属性时是否覆盖
    _set_dict 设置属性的字典数据
    _suffix_ini 支持的config 文件中的后缀列表
    _suffix  文件后缀
    context  上下文信息， 默认字典形式
    """
    ban = ['_suffix_ini', 'root_func']

    @staticmethod
    def init() -> dict:
        """
        设置基础配置
        """
        _error: bool = False
        _suffix_ini: Tuple[str, str, str] = ('.ini', '.cfg', '.conf')
        return locals()


class Setting(ParkLY):
    _name = 'Setting'
    paras = SettingParas()

    def open(self, path: str, **kwargs) -> Any:
        """
        加载配置文件, 支持ini、json、py、txt
        :param path: 需要加载配置文件的路径
        :param kwargs:
        :return : 对象本身
        """
        set_list = []
        _, suffix = os.path.splitext(path)
        suffix: str = suffix.lower()
        if suffix == '.py':
            with open(path, 'r', encoding=kwargs.get("encoding", None)) as f:
                file = f.read()
                d = readPy(file)
                d.pop('file')
                # self.paras._set_dict = {**self.paras._set_dict, **d}
                set_list += list(d.items())
        elif suffix == '.json':
            with open(path, 'r', encoding=kwargs.get("encoding", None)) as f:
                # self.paras._set_dict = {**self.paras._set_dict, **json.load(f)}
                set_list += list(json.load(f).items())
                f.close()
        elif suffix in self.paras._suffix_ini:
            config = configparser.ConfigParser()
            config.read(path, encoding='utf-8')
            d = {}
            for item in config:
                if config.has_section(item):
                    d[item] = dict(config.items(item))
            # self.paras._set_dict = {**self.paras._set_dict, **d}
            set_list += list(d.items())
        elif suffix == '.txt':
            d = {}
            with open(path, 'r', encoding=kwargs.get("encoding", None)) as f:
                lines = f.readlines()
            for line in lines:
                try:
                    key, value = line.split("=")
                    key = key.strip()
                    d[key] = value.strip()
                except Exception as e:
                    warning(f"({line})该行配置错误({e})", warn=True)
                    continue
            # self.paras._set_dict = {**self.paras._set_dict, **d}
            set_list += list(d.items())
        else:
            raise IOError(f"暂不支持该格式({suffix})配置文件")
        self.paras.update({
            '_attrs': set_list
        })
        return self

    @_
    def reckon_by_time(self):
        pass