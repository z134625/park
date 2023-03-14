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
    _Context,
    update_changeable_var,
)
from .env import env
from ._type import _Paras


class Paras(_Paras):
    """
    配置基础类
    含有参数
    ALLOW 默认允许 设置属性
    ALLOW_SET 表示允许随时修改属性 设置属性
    """
    # 配置方法权限
    ALLOW: bool = False
    # 允许设置修改的属性
    ALLOW_SET: list = []
    # 配置中的设置， 不允许修改的列表
    BAN: List[str] = []
    # 默认配置中， 不允许修改的列表
    _BAN: List[str] = ['_set_list', '_obj']
    PARK_PARAS = True

    def __init__(
            self,
            allow: bool = True,
            **kwargs: dict
    ):
        """
        默认初始化时允许设置属性
        """
        # 获取配置字典
        init = self.init()
        _init = self._init()
        _attrs = _init.get('ATTRS', {})
        attrs = init.get('ATTRS', {})
        attrs = {**attrs, **_attrs}
        set_dict = {**self._init(), **self.init()}
        set_dict.update({'ATTRS': attrs})
        self.set_paras(allow=allow, kwargs=set_dict)

    @staticmethod
    def init() -> dict:
        # 增加的配置
        return {}

    @staticmethod
    def _init() -> dict:
        # 系统基础配置
        # 对象的root权限
        ROOT: bool = False
        # 一些警告，默认开启
        WARN: bool = False
        # 设置属性时，是否覆盖 默认开启
        COVER: bool = True
        # 当对象获取属性时，是否报错 默认开启
        ERROR: bool = True
        # 设置属性的列表， 在设置成功后将删除
        SET_LIST: List[str] = []
        # 设置成功的属性和值
        ATTRS: dict = {
            'is_save_log': True,
            'save_path': '',
            'SAVE_PATH': '',
            'save_suffix': {},
            'SAVE_SUFFIX': {
                'file': '',
                'log': 'log'
            },
            'save_io': [],
            'IO_TYPE': {'file', 'log'},
            'save_mode': '',
            'SAVE_MODE': 'w',
            'save_encoding': '',
            'SAVE_ENCODING': 'utf-8',
            'speed_info': {},
            'test_info': {},
        }
        # 配置上下文
        context: _Context = _Context({})
        flags: _Context = _Context({})
        # 管理员权限方法
        root_func: List[str] = []
        OBJ: str = None
        return locals()

    def set_paras(
            self,
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
        self.ALLOW = allow
        try:
            if sys._getframe(1).f_code.co_name == 'update':
                if is_obj:
                    OBJ = kwargs.get('OBJ', None)
                    kwargs = {'OBJ': OBJ}
                else:
                    pop_keys = []
                    for key in kwargs.keys():
                        if key not in self.ALLOW_SET:
                            pop_keys.append(key)
                    for key in pop_keys:
                        kwargs.pop(key)
            if sys._getframe(1).f_code.co_name in ('update', '__init__'):
                if 'ATTRS' in kwargs:
                    attrs = kwargs.get('ATTRS', {})
                    if isinstance(attrs, (list, tuple)):
                        kwargs.update({
                            'SET_LIST': attrs
                        })
                    elif isinstance(attrs, dict):
                        kwargs.update({
                            'SET_LIST': list(attrs.items())
                        })
                    sys_attrs = self._attrs if self._attrs else {}
                    if sys._getframe(1).f_code.co_name == '__init__':
                        kwargs['ATTRS'] = attrs
                    else:
                        kwargs['ATTRS'] = {**sys_attrs}
                pattern = re.compile(r'^attrs_([a-zA-Z_]+)')
                SET_LIST = kwargs.get('SET_LIST', [])
                for key in kwargs.keys():
                    res = re.search(pattern, key)
                    if res:
                        attr = res.group(1)
                        SET_LIST.append((attr, kwargs[key]))
                if self.SET_LIST:
                    SET_LIST += self.SET_LIST
                    SET_LIST.reverse()
                kwargs.update({
                    'SET_LIST': SET_LIST
                })
                setAttrs(self, warn=False, self=sel, **kwargs)
                if sys._getframe(1).f_code.co_name == '__init__':
                    for key in kwargs.keys():
                        if key not in self.ALLOW_SET:
                            self.ALLOW_SET.append(key)
                        self.ALLOW_SET = list(set(self.ALLOW_SET))
                    for key in set(self.BAN + self._BAN):
                        if key in self.ALLOW_SET:
                            self.ALLOW_SET.remove(key)
                self._update(sel=sel)

        except Exception as e:
            warning(f"属性设置失败 原因：{e}", warn=True)
            raise e
        finally:
            self.ALLOW = False

    def _get_cls_dir(
            self,
            obj: Any = None
    ) -> List[str]:
        """
        获取self对象包含的 方法
        """
        if obj:
            return dir(obj)
        return self.ALLOW_SET

    def __setattr__(
            self,
            key: str,
            value: Any
    ):
        """
        该类不允许设置除 _allow 权限的属性
        若需要增加设置的属性
        则需要继承下 修改_allow_set 列表
        """
        if key == 'ALLOW' and sys._getframe(1).f_code.co_name != 'set_paras' or \
                key == 'ROOT' and sys._getframe(1).f_code.co_name != 'setAttrs':
            raise AttributeError('该类不允许设置属性(%s)' % key)
        elif key not in ('ALLOW', 'ROOT'):
            if key not in self.ALLOW_SET and not self.ALLOW:
                raise AttributeError('该类不允许设置属性(%s)' % key)
        return super(Paras, self).__setattr__(key, value)

    def update(
            self,
            kwargs: dict,
            sel: bool = False,
            is_obj: bool = False
    ) -> _Paras:
        """
        更新配置的一些属性
        """
        self.set_paras(allow=True, kwargs=kwargs, sel=sel, is_obj=is_obj)
        return self

    def __getattr__(
            self,
            item
    ):
        if item in self._get_cls_dir() or item.startswith('__') and item.endswith('__'):
            return super(Paras, self).__getattr__(item)
        return False

    def _update(
            self,
            sel: bool = False
    ) -> Union[None]:
        if self.OBJ:
            obj = env[self.OBJ]
            obj = setAttrs(obj=obj, self=sel)
            for item in obj.save_io:
                obj.IO_TYPE.add(item)
            obj.SAVE_SUFFIX.update(obj.save_suffix)
            obj.SAVE_PATH = obj.save_path if obj.save_path else obj.SAVE_PATH
            obj.SAVE_ENCODING = obj.save_encoding if obj.save_encoding else obj.SAVE_ENCODING
            obj.SAVE_MODE = obj.save_mode if obj.save_mode else obj.SAVE_MODE
            return obj
        return None

    def inherit_update(self, _O):
        objs = _O
        if not isinstance(_O, (list, tuple)):
            objs = [_O]
        all_attrs = {}
        _attrs = {}
        _context = _Context()
        _flags = {}
        for obj in objs:
            if isinstance(obj, Paras):
                all_attrs.update(obj.init())
                _attrs.update(obj.ATTRS)
                _context.update(obj.context)
                _flags.update(obj.flags)
                update_changeable_var(old={'ATTRS': _attrs,
                                           'context': _context,
                                           'flags': _flags,
                                           },
                                      new=all_attrs,
                                      var=['ATTRS', 'context', 'flags'])

        old = {
            'ATTRS': self.ATTRS,
            'context': self.context,
            'flags': self.flags,
        }
        update_changeable_var(old, all_attrs, var=['ATTRS', 'context', 'flags'])
        self.update(all_attrs)
