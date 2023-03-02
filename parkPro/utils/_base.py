from typing import (
    Union,
    Tuple,
    List,
    Any
)

from .paras import Paras
from .env import env, Io
from .api import reckon_by_time_run
from ..tools import _Context


def update_attrs_dict(
        name: str,
        K: dict,
        attrs: dict
) -> dict:
    """
    用于更新属性中字典，避免同名覆盖
    例如:
    attrs = {'a': {'b': 1}}
    K = {'a': {'c': 1}}
    attrs.update(K) -> {'a': {'c': 1}}
    update_attrs_dict('a', K, attrs) -> {'a': {'c': 1, 'b': 1}}
    """
    if name in attrs:
        attrs[name].update(K)
    else:
        attrs[name] = K
    return attrs


def update_changeable_var(
        old: dict,
        new: dict,
        var=None
):
    """
    该方法用于 对var中的键 做出可变修改
    与update_attrs_dict一致
    """
    if var is None:
        var = []
    for v in var:
        update_attrs_dict(v, old.get(v), new)
        old.pop(v)
    new.update(old)


def _inherit_parent(
        inherits: Union[str, List[str], Tuple[str]],
        attrs: dict
) -> Tuple[Tuple[Any], dict]:
    """
    用于查找父类并从父类继承属性，
    """
    bases = []
    all_attrs = {}
    _attrs = {}
    _context = _Context()
    _flags = {}
    if isinstance(inherits, str):
        parent = env[attrs.get('_inherit')]
        if not isinstance(parent, Basics):
            parent = parent.__class__
        bases = (parent,)
        all_attrs.update(parent.paras.init())
        _attrs.update(parent.paras.ATTRS)
        _context.update(parent.paras.context)
        _flags.update(parent.paras.flags)
        update_changeable_var(old={'ATTRS': _attrs,
                                   'context': _context,
                                   'flags': _flags,
                                   },
                              new=all_attrs,
                              var=['ATTRS', 'context', 'flags'])
        if 'paras' in attrs and isinstance(attrs['paras'], Paras):
            old = {**attrs['paras']._init(), **attrs['paras'].init()}
            update_changeable_var(old, all_attrs, var=['ATTRS', 'context', 'flags'])
            attrs['paras'].update(all_attrs)
        else:
            paras = Paras()
            paras.update(all_attrs)
            attrs['paras'] = paras
    elif isinstance(inherits, (tuple, list)):
        for inherit in inherits:
            parent = env[inherit]
            if not isinstance(parent, Basics):
                parent = parent.__class__
            all_attrs.update(parent.paras.init())
            _attrs.update(parent.paras.ATTRS)
            _context.update(parent.paras.context)
            _flags.update(parent.paras.flags)
            update_changeable_var(old={'ATTRS': _attrs,
                                       'context': _context,
                                       'flags': _flags,
                                       },
                                  new=all_attrs,
                                  var=['ATTRS', 'context', 'flags'])
            bases += [parent]
        if 'paras' in attrs and isinstance(attrs['paras'], Paras):
            old = {**attrs['paras']._init(), **attrs['paras'].init()}
            update_changeable_var(old, all_attrs, var=['ATTRS', 'context', 'flags'])
            attrs['paras'].update(all_attrs)
        else:
            paras = Paras()
            paras.update(all_attrs)
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
