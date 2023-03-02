import sys
import logging
from collections.abc import Iterable
from io import (
    StringIO,
    BytesIO
)
from typing import (
    Union,
    List
)

from ..tools import warning
from ._type import _ParkLY


class RegisterEnv:
    __slots__ = (
        'log',
        '_mapping',
        '_mapping_info',
        'ios',
        '_register_info',
        '_ios'
    )

    def __init__(
            self
    ):
        self._mapping: dict = {}
        self._mapping_info: dict = {}
        self._register_info = {}
        self.ios = {
            'log': StringIO(),
            'file': BytesIO(),
            'str': StringIO(),
        }
        self.log = logging

    def init_log_config(
            self,
            level: int,
            show: bool,
    ) -> logging.Logger:
        if not level:
            level = logging.DEBUG
        logger = logging.getLogger(__file__)
        logger.setLevel(level)

        fh = logging.StreamHandler(sys.stderr)
        fh.setLevel(level)
        ch = logging.StreamHandler(self.ios['log'])
        ch.setLevel(level)
        formatter = logging.Formatter("[%(name)s]-[%(levelname)s]: [%(pathname)s](%(filename)s:%(module)s) \n"
                                      "\t%(funcName)s - %(lineno)d \t : %(asctime)s \n"
                                      "\tmsg: %(message)s",
                                      datefmt="%Y-%m-%d %H:%M:%S")
        ch.setFormatter(formatter)
        fh.setFormatter(formatter)
        if show:
            logger.addHandler(fh)
        logger.addHandler(ch)
        return logger

    def __call__(
            self,
            name: str,
            cl,
            warn: bool = True,
            inherit: bool = False
    ):
        self._register(
            name=name,
            cl=cl,
            warn=warn,
            inherit=inherit
        )

    def _register(
            self,
            name: str,
            cl,
            warn: bool = True,
            inherit: bool = False
    ):
        if name in self._mapping and not inherit:
            warning('该注册名(%s)已存在， 将覆盖旧的应用' % name, warn=warn)
        self._mapping.update(
            {name: cl}
        )
        parents = cl.__bases__ if hasattr(cl, '__bases__') else cl.__class__.__bases__
        if not isinstance(parents, Iterable):
            parents = [parents]
        for parent in parents:
            k = (hasattr(parent, '_name') and parent._name) or parent.__name__
            if k in self._mapping_info and k != cl._name and cl._name not in self._mapping_info[k]:
                self._mapping_info[k].append(cl._name)
            elif k != cl._name:
                self._mapping_info[k] = [cl._name]
        if inherit:
            def update_attrs(k1):
                for item in self._mapping_info.get(k1, []):
                    if item in self._mapping:
                        bases = []
                        _bases = self[item].__bases__
                        for base in _bases:
                            if base._name == cl._name:
                                bases.append(cl)
                            else:
                                bases.append(base)
                        setattr(self[item], '__bases__', tuple(bases))
                        self[item].__bases__ = tuple(bases)
                    if item in self._mapping_info:
                        update_attrs(item)

            update_attrs(name)

    def __setattr__(
            self,
            key,
            value
    ):
        if key == '_mapping' and sys._getframe(1).f_code.co_name != '__init__':
            raise AttributeError("不允许设置该属性%s" % key)
        return super(RegisterEnv, self).__setattr__(key, value)

    def __getitem__(
            self,
            item: str
    ) -> _ParkLY:
        if item in self._mapping:
            return self._mapping[item]
        raise KeyError('没有注册该配置(%s)' % item)

    def load(
            self,
            level: Union[None, int] = None,
            _type: str = None,
            show: bool = True
    ) -> None:
        for key in self._mapping:
            if getattr(self._mapping[key], '_park_Basics'):
                _class = self._mapping[key]
                if _type and getattr(_class, '_type', None) == _type:
                    self._mapping[key]()
                else:
                    self._mapping[key]()
        self.log = self.init_log_config(level, show)

    def clear(
            self
    ) -> None:
        return self._mapping.clear()

    @property
    def apps(
            self
    ) -> List[str]:
        return list(self._mapping.keys())


class Io:
    _io_key = None
    _io = None

    def __call__(
            self,
            io_id: str = None
    ):
        self._io_key = io_id
        self._io = env.ios.get(io_id, None)
        return self

    def __getitem__(
            self,
            item: str
    ):
        return Io()(io_id=item)

    def clear(
            self
    ) -> None:
        if self._io:
            io_obj = env.ios[self._io_key]
            env.ios[self._io_key] = io_obj.__class__()

    def write(
            self,
            msg: str
    ) -> None:
        self._io.write(msg)

    def getvalue(
            self
    ) -> Union[str, bytes]:
        return self._io.getvalue()


env = RegisterEnv()
