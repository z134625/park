from typing import Union

from . import ormbase
from . import model
from .model_env import model_env
from ...utils.env import RegisterEnv
from .. import setting


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
        if callable(_class) and getattr(_class, '_type', None) == _type:
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
        model_env.load()


RegisterEnv.load = load