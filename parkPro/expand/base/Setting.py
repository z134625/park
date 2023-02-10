import configparser
import json
import os
from typing import Union, Any

from .paras import SettingParas
from ...utils.base import ParkLY
from ...tools import (
    readPy,
    warning,
    _Context
)


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

    @property
    def setting(self) -> _Context:
        return self._setting

    def _load_setting(self,
                      path: str,
                      **kwargs: dict
                      ) -> object:
        """
        加载配置文件, 支持ini、json、py、txt
        :param path: 需要加载配置文件的路径
        :param kwargs:
        :return : 对象本身
        """
        self._setting = _Context({})
        if path:
            set_list = []
            _, suffix = os.path.splitext(path)
            suffix: str = suffix.lower()
            if suffix == '.py':
                file = self.open(path, encoding=kwargs.get("encoding", None))
                d = readPy(file)
                d.pop('file')
                set_list += list(d.items())
            elif suffix == '.json':
                f = self.open(path,
                              mode='r',
                              encoding=kwargs.get("encoding", None),
                              get_file=True
                              )
                set_list += list(json.load(f).items())
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
                lines = self.open(file=path,
                                  encoding=kwargs.get("encoding", None),
                                  lines=True)
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
            self._setting.update(dict(set_list))
            self.paras.update({
                '_attrs': set_list
            })
        return self

    def give(self,
             obj: Union[Any],
             content: dict = None
             ):
        """
        此方法用于将自身属性给予给出的参数
        不提供content 则将自身的 新增的属性赋给 obj对象
        content 必须为字典形式
        以 key 变量名， value 变量值 可以为方法， 也可以为值
        """
        if not content:
            if isinstance(obj, ParkLY):
                obj.update({
                    'setting': self.setting
                })
                return obj
            return self
        else:
            assert isinstance(content, dict)
            for key, value in content.items():
                if callable(value):
                    setattr(obj, key, value)
                else:
                    setattr(obj, key, value)
            obj.paras._attrs.update(content)
            return self
