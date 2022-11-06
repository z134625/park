import json
import logging
import os
import re
import shutil
import sys
import copy
import pickle
import warnings
import configparser
from io import BytesIO, StringIO

from typing import Union, List, Any, Tuple, Set
from types import MethodType, FunctionType
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


def get_size(obj, seen=None):
    # From
    # Recursively finds size of objects
    size = sys.getsizeof(obj)
    if seen is None:
        seen = set()
    obj_id = id(obj)
    if obj_id in seen:
        return 0
    # Important mark as seen *before* entering recursion to gracefully handle
    # self-referential objects
    seen.add(obj_id)
    if isinstance(obj, dict):
        size += sum([get_size(v, seen) for v in obj.values()])
        size += sum([get_size(k, seen) for k in obj.keys()])
    elif hasattr(obj, '__dict__'):
        size += get_size(obj.__dict__, seen)
    elif hasattr(obj, '__iter__') and not isinstance(obj, (str, bytes, bytearray)):
        size += sum([get_size(i, seen) for i in obj])
    return size


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


class RegisterEnv:
    __slots__ = ('_mapping',)

    def __init__(self):
        self._mapping: dict = {}

    def __call__(self, name, cl, warn=True, inherit=False):
        self._register(name=name, cl=cl, warn=warn, inherit=inherit)

    def _register(self, name, cl, warn, inherit):
        if name in self._mapping and not inherit:
            warning('该注册名(%s)已存在， 将覆盖旧的应用' % name, warn=warn)
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

    @property
    def apps(self):
        return list(self._mapping.keys())


env = RegisterEnv()


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
        _obj: str = None
        return locals()

    def _set_paras(self, allow: bool = True, kwargs: dict = None, sel=False, is_obj=False) -> None:
        """
        修改属性方法，
        """
        if kwargs is None:
            kwargs = {}
        self._allow = allow
        try:
            if sys._getframe(1).f_code.co_name == 'update':
                if is_obj:
                    _obj = kwargs.get('_obj', None)
                    kwargs = {'_obj': _obj}
                else:
                    pop_keys = []
                    for key in kwargs.keys():
                        if key not in self._allow_set:
                            pop_keys.append(key)
                    for key in pop_keys:
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
                    if sys._getframe(1).f_code.co_name == '__init__':
                        kwargs['_attrs'] = attrs
                    else:
                        kwargs['_attrs'] = {**sys_attrs}
                pattern = re.compile(r'^attrs_([a-zA-Z_]+)')
                _set_list = kwargs.get('_set_list', [])
                for key in kwargs.keys():
                    res = re.search(pattern, key)
                    if res:
                        attr = res.group(1)
                        _set_list.append((attr, kwargs[key]))
                if self._set_list:
                    _set_list += self._set_list
                    _set_list.reverse()
                kwargs.update({
                    '_set_list': _set_list
                })
                setAttrs(self, warn=False, self=sel, **kwargs)
                if sys._getframe(1).f_code.co_name == '__init__':
                    for key in kwargs.keys():
                        if key not in self._allow_set:
                            self._allow_set.append(key)
                        self._allow_set = list(set(self._allow_set))
                    for key in set(self.ban + self._ban):
                        if key in self._allow_set:
                            self._allow_set.remove(key)
                self._update(sel=sel)

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

    def update(self, kwargs: dict, sel=False, is_obj=False) -> Any:
        """
        更新配置的一些属性
        """
        self._set_paras(allow=True, kwargs=kwargs, sel=sel, is_obj=is_obj)
        return self

    def __getattr__(self, item):
        if item in self._get_cls_dir() or item.startswith('__') and item.endswith('__'):
            return super(Paras, self).__getattr__(item)
        else:
            return False

    def _update(self, sel=False):
        if self._obj:
            obj = env[self._obj]
            return setAttrs(obj=obj, self=sel)
        return None


class command(object):
    """

    """
    __slots__ = ('keyword', 'args', 'func')

    def __init__(self, keyword):
        self.keyword = keyword

    def __call__(self, func):
        self.func = func
        return self

    def __get__(self, obj, klass=None):
        if isinstance(obj, Tools):
            func = MethodType(self.func, obj)
            return obj._command(func, self.keyword)


class monitorV(object):
    """
    监控装饰器， 配合监控方法MonitorV 使用 用于监控 对象中变量修改 即触发__set__ 时
    @monitor('var')
    def test(self):
        return None
    在此案例中 默认监控 var变量， 当var 触发__set__ 方法时 同时将触发test
    """
    __slots__ = ('fields', 'args', 'func')

    def __init__(self, fields):
        self.fields = fields

    def __call__(self, func):
        self.func = func
        return self

    def __get__(self, obj, klass=None):
        if isinstance(obj, Monitor) and isinstance(obj, Tools) and isinstance(self.func, command):
            func = MethodType(self.func.func, obj)
            return obj._monitoringV(func, self.fields, keyword=self.func.keyword)
        elif isinstance(obj, Monitor):
            return obj._monitoringV(self.func, self.fields)
        return obj


class monitor(object):
    """
    监控装饰器， 配合监控方法Monitor 使用
    @monitor('monitor1')
    def test(self):
        return None
    在此案例中 没当test执行时， 都将调用 monitor1 的监控方法，
    若监控方法 中需要test 的返回值时， monitor1 中可以直接使用 self._return 获取
    默认得 _return  是为False
    monitor 的监控方法需要传参时 可在后加上参数， 即
    def monitor1(self, args1, kwargs1):
        pass
    @monitor('monitor1', 1, 2)
    def test(self):
        return None
    """
    __slots__ = ('field', 'args', 'func')

    def __init__(self, field, *args, **kwargs):
        self.field = field
        self.args = (args, kwargs)

    def __call__(self, func):
        self.func = func
        return self

    def __get__(self, obj, klass=None):
        if isinstance(obj, Monitor) and isinstance(obj, Tools) and isinstance(self.func, command):
            func = MethodType(self.func.func, obj)
            res = obj._monitoring(func, self.field, self.args, keyword=self.func.keyword)
            return res
        elif isinstance(obj, Monitor):
            func = MethodType(self.func, self)
            res = obj._monitoring(func, self.field, self.args)
            return res
        return obj


class Basics(type):

    def __new__(mcs, name, bases, attrs):
        """
        重组定义的类，
        增加新的属性__new_attrs__
        添加默认属性 paras
        """
        mappings = set()
        mappings_func = set()
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
                    if isinstance(val, (monitorV, monitor, command)):
                        mappings_func.add(key)
                    mappings.add(key)
        attrs['__new_attrs__'] = mappings
        attrs['__new_attrs_decorator_func__'] = mappings_func
        res = type.__new__(mcs, name, bases, attrs)
        if attrs.get('_name') and attrs.get('_inherit'):
            inherits = attrs.get('_inherit')
            if isinstance(inherits, str):
                parent = env[attrs.get('_inherit')]
                if not isinstance(parent, Basics):
                    parent = parent.__class__
                bases = (parent,)
            elif isinstance(inherits, (tuple, list)):
                bases = []
                _attrs = {}
                for inherit in inherits:
                    parent = env[inherit]
                    if not isinstance(parent, Basics):
                        parent = parent.__class__
                    _attrs.update(parent.paras._attrs)
                    bases += [parent]
                if 'paras' in attrs and isinstance(attrs['paras'], Paras):
                    attrs['paras'].update({
                        '_attrs': _attrs
                    })
                else:
                    paras = bases[-1].paras
                    paras.update({
                        '_attrs': _attrs
                    })
                    attrs['paras'] = paras
                bases = tuple(bases)
            res = type.__new__(mcs, name, bases, attrs)
            env(name=attrs.get('_name'), cl=res)
        elif attrs.get('_name'):
            env(name=attrs.get('_name'), cl=res)
        elif attrs.get('_inherit'):
            inherit = attrs.get('_inherit')
            if isinstance(inherit, (tuple, list)):
                inherit = inherit[0]
            parent = env[inherit]
            if not isinstance(parent, Basics):
                parent = parent.__class__
            bases = (parent,)
            res = type.__new__(mcs, name, bases, attrs)
            env(name=inherit, cl=res, inherit=True)
        setattr(res, 'env', env)
        return res


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

    def __call__(self, func=None, root: bool = False):
        """
        增加属性方法
        root 将对增加的方法施加管理员权限，
        当开启管理设置、 或自身方法调用时将不做限制
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
                        (
                         call_name not in self.__new_attrs__ and
                         call_name not in dir(ParkLY)
                        ):
                    if not self.paras._root and (hasattr(res, '__self__') and not isinstance(res.__self__, ParkLY)):
                        raise AttributeError('此方法(%s)为管理员方法，不可调用' % item)
                return res
            elif item.startswith("_") and not self.paras._root and \
                    (
                     call_name not in self.__new_attrs__ and
                     call_name not in (dir(self))
                    ):
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
    """
    设置文件方法，
    新增open方法 可以加载路径的配置文件并赋予给自身对象
    注： 默认的 以_开头的变量将被定义为 私有属性
    若需要获取此私有属性， 可调用 obj.sudo()._a 即可
    默认的在继承中 将不会对这进行限制
    """
    _name = 'setting'
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



class MonitorParas(Paras):
    """
    监控方法的配置，
    默认将添加_return 参数，
    该参数用于获取被监控方法的返回值
    """
    ban = ['_error', 'context', '_root']

    @staticmethod
    def init():
        _attrs = {'_return': False,
                  '_funcName': None,
                  '_monitor_fields': [],
                  '_monitor_func': {},
                  }
        _error = False
        _root = True
        _warn = False
        return locals()


class Monitor(ParkLY):
    """
    监控主要类
    使用方式
>>>    class Test(ParkLY):
>>>        _inherit = 'monitor'
>>>
>>>        @monitor('monitor1')
>>>        def test1(self):
>>>            return 100
>>>
>>>        def monitor1(self):
>>>            print(self._return)
>>>    test = Test()
>>>    test.test1()
>>>    100
    """
    _name = 'monitor'
    paras = MonitorParas()

    def init(self, **kwargs):
        res = super(Monitor, self).init(**kwargs)
        for f in dir(self):
            if (not (f.startswith('__') and f.endswith('__'))) and f in self.__new_attrs_decorator_func__:
                eval(f'self.{f}')
        return res

    def _monitoring(self, func, monit, arg, keyword=None):
        if keyword:
            if isinstance(keyword, str):
                self._command_keyword[keyword] = keyword + '$'
                self._command_keyword_help[keyword + '$'] = func.__doc__ or '没有使用帮助'
                self._command_func[keyword + '$'] = func.__name__
            elif isinstance(keyword, (tuple, list)):
                keyword = sorted(keyword)
                keyword.reverse()
                keys = '$'.join(keyword)
                for key in keyword:
                    self._command_keyword[key] = keys
                self._command_keyword_help[keys] = func.__doc__ or '没有使用帮助'
                self._command_func[keys] = func.__name__

        def monitoring_warps(*args, **kwargs):
            res = func(*args, **kwargs)
            self._return = res
            if isinstance(monit, str):
                monit_func = getattr(self, monit)
                self._funcName = func.__name__
                monit_func(*arg[0], **arg[1])
            elif isinstance(monit, (list, tuple, set)):
                for f in monit:
                    monit_func = getattr(self, f)
                    self._funcName = func.__name__
                    monit_func(*arg[0], **arg[1])
            self._funcName = None
            self._return = False
            return res

        return monitoring_warps

    def _monitoringV(self, func, monit, keyword=None):
        self._monitor_fields.append(monit)
        self._monitor_func[monit] = func.__name__
        if keyword:
            if isinstance(keyword, str):
                self._command_keyword[keyword] = keyword + '$'
                self._command_keyword_help[keyword + '$'] = func.__doc__ or '没有使用帮助'
                self._command_func[keyword + '$'] = func.__name__
            elif isinstance(keyword, (tuple, list)):
                keyword = sorted(keyword)
                keyword.reverse()
                keys = '$'.join(keyword)
                for key in keyword:
                    self._command_keyword[key] = keys
                self._command_keyword_help[keys] = func.__doc__ or '没有使用帮助'
                self._command_func[keys] = func.__name__

        def monitoringV_warps(*args, **kwargs):
            res = func(*args, **kwargs)
            return res

        return monitoringV_warps

    def __setattr__(self, key, value):
        res = super(Monitor, self).__setattr__(key=key, value=value)
        if key in self._monitor_fields:
            func = self._monitor_func[key]
            func = eval(f'self.{func}')
            func()
        return res


class ToolsParas(Paras):
    """
    工具配置
    """

    @staticmethod
    def init():
        _attrs = {
            '_command_keyword_help': {},
            '_command_func': {},
            '_command_keyword': {},
        }
        _root = True
        return locals()


class Tools(ParkLY):
    _name = 'tools'
    paras = ToolsParas()

    def init(self, **kwargs):
        """
        初始化，用于对配置进行注册
        """
        res = super(Tools, self).init(**kwargs)
        for f in dir(self):
            if not (f.startswith('__') and f.endswith('__')) and (f in self.__new_attrs_decorator_func__):
                eval(f'self.{f}')
        eval('self.help')
        return res

    def _command(self, func, keyword):
        """
        装饰器 用于封装， 命令启动程序
        配置类command 装饰器使用
        """
        if isinstance(keyword, str):
            self._command_keyword[keyword] = keyword + '$'
            self._command_keyword_help[keyword + '$'] = func.__doc__ or '没有使用帮助'
            self._command_func[keyword + '$'] = func.__name__
        elif isinstance(keyword, (tuple, list)):
            keyword = sorted(keyword)
            keyword.reverse()
            keys = '$'.join(keyword)
            for key in keyword:
                self._command_keyword[key] = keys
            self._command_keyword_help[keys] = func.__doc__ or '没有使用帮助'
            self._command_func[keys] = func.__name__

        def command_warps(*args, **kwargs):
            res = func(*args, **kwargs)
            return res

        return command_warps

    @staticmethod
    def progress(enum=True, epoch_show=True, log_file=None):
        io = StringIO()
        file = log_file

        logging.basicConfig(filemode='w', level=logging.DEBUG,
                            format="[%(name)s]-[%(levelname)s]: [%(pathname)s](%(filename)s:%(module)s) \n" \
                                   "\t%(funcName)s - %(lineno)d \t : %(asctime)s \n" \
                                   "\tmsg: %(message)s",
                            stream=io)

        class _ParkProgress(object):

            def __init__(self, files, epoch_show_):
                self.file = files
                self.epoch_show = epoch_show_

            def __call__(self, obj, start=0, step=1):
                self.obj = [item for item in obj]
                self._start = start
                self._step = step
                self._length = len(self.obj)
                return self

            def __iter__(self):
                return self

            def __next__(self):
                self._start += self._step
                if self._start > self._length:
                    raise StopIteration
                else:
                    res = self.obj[self._start - self._step]
                    if enum:
                        res = (self._start - self._step, self.obj[self._start - 1])
                    return res

            def epoch(self, msg=None, typ=True, start=False):
                log = logging.debug
                if not start:
                    msgs = f"\033[1;32;32m\r当前迭代第{self._start}，{msg or '....'}\033[0m\n"
                    if not typ:
                        log = logging.error
                        msgs = f"\033[1;31;31m\r当前迭代第{self._start}，{msg or '....'}\033[0m\n"
                    log(f"""当前迭代第{self._start}，{msg or '....'}""")
                else:
                    msgs = f"\033[1;31;31m\r当前正迭代第{self._start}个中....\033[0m"
                if self.epoch_show:
                    print(msgs, end='', flush=True)

            def epochs(self, func, args=None, error=None, success=None):
                try:
                    self.epoch(start=True)
                    if isinstance(args, (tuple, list)):
                        if len(args) == 2 and isinstance(args[0], tuple) and isinstance(args[0], dict):
                            res = func(*args[0], **args[1])
                        else:
                            res = func(*args)
                    elif args:
                        res = func(args)
                    else:
                        res = func()
                    res = True, res
                except Exception as e:
                    self.epoch(msg=error or
                                   f"该程序({func.__name__ if hasattr(func, '__name__') else str(func)})执行失败",
                               typ=False)
                    res = False, str(e)
                else:
                    self.epoch(msg=success or
                                   f"该程序({func.__name__ if hasattr(func, '__name__') else str(func)})执行成功",
                               typ=True)
                finally:
                    return res

            @staticmethod
            def success(msg=None):
                msgs = '\n' + (msg or '成功！')
                logging.debug(msgs)
                print(msgs)

            @staticmethod
            def error(msg=None):
                msgs = '\n' + (msg or '失败！')
                logging.error(msgs)
                print(msgs)

            def __enter__(self):

                return self

            def __exit__(self, exc_type, exc_val, exc_tb):
                if self.file:
                    value = io.getvalue()
                    with open(file, 'a') as f:
                        f.write('=' * 25 + 'start' + '=' * 25 + '\n')
                        f.write(value)
                        f.write('=' * 25 + 'end' + '=' * 25 + '\n')
                io.close()
                del self

        return _ParkProgress(file, epoch_show)

    @command(['-h', '--help'])
    def help(self, order=None):
        """
        此操作将打印每种方法的帮助信息
        """
        if not order:
            keyword = self._command_keyword
            keys = set(map(lambda x: keyword[x], keyword.keys()))
            for key in sorted(keys):
                strs = key.replace('$', '\t')
                print(f"""{strs}: \n {self._command_keyword_help[key]}""")
        else:
            if order in self._command_keyword_help:
                print(f"""{order}: \n {self._command_keyword_help[order]}""")
            else:
                print(f"""{order}: \n 没有该帮助， 请检查""")

    def main(self):
        """
        命令行启动主程序
        """
        commands = sys.argv[1:]
        error = []
        with self.progress(enum=True, epoch_show=True, log_file='./tt.log') as pg:
            command_keyword = self._command_keyword
            items = map(lambda x: command_keyword[x],
                        filter(lambda x: x in command_keyword, commands))

            for i, keys in pg(items):
                args = tuple()
                index = i + 1
                if index < len(commands) and commands[index] not in command_keyword:
                    args = (commands[index],)
                if '-h' in commands or '--help' in commands:
                    if '-h' in commands:
                        index = commands.index('-h') + 1
                    else:
                        index = commands.index('--help') + 1
                    if index < len(commands) and commands[index]:
                        args = (commands[index],)
                    self.help(*args)
                    break
                func = self._command_func[keys]
                func = eval(f'self.{func}')
                res = pg.epochs(func=func, args=args)
                if not res[0]:
                    error.append(res[1])
            if not error:
                return pg.success()
            else:
                return pg.error(msg='\n'.join(error))
