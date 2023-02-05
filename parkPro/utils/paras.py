import datetime
import re
import sys
from typing import (
    List,
    Any,
    Union
)

from ..tools import (
    setAttrs,
    warning,
    _Context
)
from .env import env


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
    _park_paras = True

    def __init__(self,
                 allow: bool = True,
                 **kwargs: dict
                 ):
        """
        默认初始化时允许设置属性
        """
        # 获取配置字典
        init = self.init()
        _init = self._init()
        _attrs = _init.get('_attrs', {})
        attrs = init.get('_attrs', {})
        attrs = {**attrs, **_attrs}
        set_dict = {**self._init(), **self.init()}
        set_dict.update({'_attrs': attrs})
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
        _warn: bool = False
        # 设置属性时，是否覆盖 默认开启
        _cover: bool = True
        # 当对象获取属性时，是否报错 默认开启
        _error: bool = True
        # 设置属性的列表， 在设置成功后将删除
        _set_list: List[str] = []
        # 设置成功的属性和值
        _attrs: dict = {
            'is_save_log': True,
            'save_path': '',
            '_save_path': '',
            'save_suffix': {},
            '_save_suffix': {
                'file': '',
                'log': 'log'
            },
            'save_io': [],
            '_save_io': {'file', 'log'},
            'save_mode': '',
            '_save_mode': 'w',
            'save_encoding': '',
            '_save_encoding': 'utf-8',
            'speed_info': {},
            'test_info': {},
        }
        # 配置上下文
        context: _Context = _Context({})
        flags: _Context = _Context({})
        # 管理员权限方法
        root_func: List[str] = []
        _obj: str = None
        return locals()

    def _set_paras(self,
                   allow: bool = True,
                   kwargs: dict = None,
                   sel: bool = False,
                   is_obj: bool = False
                   ) -> None:
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

    def _get_cls_dir(self,
                     obj: Any = None
                     ) -> List[str]:
        """
        获取self对象包含的 方法
        """
        if obj:
            return dir(obj)
        return self._allow_set

    def __setattr__(self,
                    key: str,
                    value: Any
                    ):
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

    def update(self,
               kwargs: dict,
               sel: bool = False,
               is_obj: bool = False
               ) -> Any:
        """
        更新配置的一些属性
        """
        self._set_paras(allow=True, kwargs=kwargs, sel=sel, is_obj=is_obj)
        return self

    def __getattr__(self, item):
        if item in self._get_cls_dir() or item.startswith('__') and item.endswith('__'):
            return super(Paras, self).__getattr__(item)
        return False

    def _update(self,
                sel: bool = False
                ) -> Union[None]:
        if self._obj:
            obj = env[self._obj]
            obj = setAttrs(obj=obj, self=sel)
            for item in obj.save_io:
                obj._save_io.add(item)
            obj._save_suffix.update(obj.save_suffix)
            obj._save_path = obj.save_path if obj.save_path else obj._save_path
            obj._save_encoding = obj.save_encoding if obj.save_encoding else obj._save_encoding
            obj._save_mode = obj.save_mode if obj.save_mode else obj._save_mode
            return obj
        return None



