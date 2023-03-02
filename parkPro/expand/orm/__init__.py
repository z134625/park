import json
from typing import Union

from . import ormbase
from . import model
from .model_env import model_env
from ...utils.env import RegisterEnv
from . import ParkFields


def load(
        self,
        level: Union[None, int] = None,
        show: bool = True,
        _type: str = 'normal',
        path: str = None
) -> None:
    s_d = {}
    cr = False
    if path and _type == 'orm':
        with open(path, 'r') as f:
            setting = json.load(f)
        ParkFields.sql_type = setting['sql_type']
        if setting.get('host'):
            s_d.update({'host': setting['host']})
        if setting.get('port'):
            s_d.update({'port': setting['port']})
        if setting.get('user'):
            s_d.update({'user': setting['user']})
        if setting.get('password'):
            s_d.update({'password': setting['password']})
        if setting.get('database'):
            s_d.update({'database': setting['database']})
        if setting.get('path'):
            s_d.update({'path': setting['path']})
        if s_d:
            if callable(self['parkOrm']):
                cr = self['parkOrm']().connect(ParkFields.sql_type, **s_d)
            else:
                cr = self['parkOrm'].connect(ParkFields.sql_type, **s_d)

    for key in self._mapping:
        if path and s_d and key == 'parkOrm':
            continue

        _class = self._mapping[key]
        if _type and getattr(_class, '_type', None) == _type:
            if callable(_class):
                self._mapping[key]()
        elif not _type and callable(_class):
            self._mapping[key]()
    if cr:
        model_env(cr=cr, E=self).load_init()
    self.log = self.init_log_config(level, show)


RegisterEnv.load = load
