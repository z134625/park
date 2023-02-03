
from typing import (
    Union,
    Tuple,
    List,
    Any
)

from .paras import Paras
from .env import env, Io
from .api import reckon_by_time_run


def _update_attrs_dict(
        name: str,
        K: dict,
        attrs: dict
) -> dict:
    if name in attrs:
        attrs[name].update(K)
    else:
        attrs[name] = K
    return attrs


def _inherit_parent(
        inherits: Union[str, List[str], Tuple[str]],
        attrs: dict
) -> Tuple[Tuple[Any], dict]:
    bases = []
    all_attrs = {}
    _attrs = {}
    _context = {}
    _flags = {}
    if isinstance(inherits, str):
        parent = env[attrs.get('_inherit')]
        if not isinstance(parent, Basics):
            parent = parent.__class__
        bases = (parent,)
        all_attrs.update(parent.paras.init())
        _attrs.update(parent.paras._attrs)
        _context.update(parent.paras.context)
        _flags.update(parent.paras.flags)
        all_attrs = _update_attrs_dict('_attrs', _attrs, all_attrs)
        all_attrs = _update_attrs_dict('context', _context, all_attrs)
        all_attrs = _update_attrs_dict('flags', _flags, all_attrs)
        if 'paras' in attrs and isinstance(attrs['paras'], Paras):
            _attr = attrs['paras']._attrs
            _context = attrs['paras'].context
            new_attrs = attrs['paras'].init()
            if '_attrs' in new_attrs:
                new_attrs.pop('_attrs')
            if 'context' in new_attrs:
                new_attrs.pop('context')
            all_attrs.update(new_attrs)
            all_attrs = _update_attrs_dict('_attrs', _attrs, all_attrs)
            all_attrs = _update_attrs_dict('context', _context, all_attrs)
            all_attrs = _update_attrs_dict('flags', _flags, all_attrs)
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
            _attrs.update(parent.paras._attrs)
            _context.update(parent.paras.context)
            all_attrs = _update_attrs_dict('_attrs', _attrs, all_attrs)
            all_attrs = _update_attrs_dict('context', _context, all_attrs)
            all_attrs = _update_attrs_dict('flags', _flags, all_attrs)
            bases += [parent]
        if 'paras' in attrs and isinstance(attrs['paras'], Paras):
            _attr = attrs['paras']._attrs
            _context = attrs['paras'].context
            new_attrs = attrs['paras'].init()
            if '_attrs' in new_attrs:
                new_attrs.pop('_attrs')
            if 'context' in new_attrs:
                new_attrs.pop('context')
            all_attrs.update(new_attrs)
            if '_attrs' in all_attrs:
                all_attrs['_attrs'].update(_attrs)
            else:
                all_attrs['_attrs'] = _attrs

            if 'context' in all_attrs:
                all_attrs['context'].update(_context)
            else:
                all_attrs['context'] = _context
            attrs['paras'].update(all_attrs)
        else:
            paras = Paras()
            paras.update(all_attrs)
            attrs['paras'] = paras
        bases = tuple(bases)
    return bases, attrs


class Basics(type):
    _park_Basics = True

    def __new__(mcs,
                name: str,
                bases: tuple,
                attrs: dict
                ):
        """
        重组定义的类，
        增加新的属性__new_attrs__
        添加默认属性 paras
        """
        mappings = set()
        _attrs = attrs.items()
        if attrs['__qualname__'] != 'ParkLY':
            if not attrs.get('_name') and not attrs.get('_inherit'):
                raise AttributeError("必须设置_name属性")
            if attrs.get('_name') and not attrs.get('_inherit'):
                if 'paras' not in attrs or ('paras' in attrs and not isinstance(attrs['paras'], Paras)):
                    attrs['paras'] = Paras()
            for key, val in _attrs:
                if key not in ['__module__', '__qualname__']:
                    attrs[key] = reckon_by_time_run(val)
                    mappings.add(key)
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
            setattr(res, '__new_attrs__', mappings.union(res.__new_attrs__))
        else:
            setattr(res, '__new_attrs__', mappings)
        return res

