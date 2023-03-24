import sys
import os
from typing import Union
import pkgutil

from . import intellect, html, orm

from ..utils.env import RegisterEnv
from .. import setting


expands = locals()


def expands_register():
    if hasattr(setting, 'expands'):
        es = setting.expands
        if isinstance(setting.expands, str) and ',' in setting.expands:
            es = list(map(lambda x: x.strip(), setting.expands.split(',')))
        for e in es:
            pass


def load(
        self,
        path: str = None,
        level: Union[None, int] = None,
        show: bool = True,
        _type: str = 'normal',
) -> None:
    _load = []
    for key in self._mapping:
        _class = self._mapping[key]
        if not _class._obj and getattr(_class, '_type', None) == 'normal':
            self._mapping[key]()
        else:
            _load.append(self._mapping[key])
    self.log = self.init_log_config(level, show)
    if path:
        obj = object()
        settings = self['setting'].load('setting', args=path).give(obj)
        for key, value in settings.items():
            setting.var[key] = value
        del obj
        for cl in _load:
            cl()
        expands_register()
        self.load()


RegisterEnv.load = load
