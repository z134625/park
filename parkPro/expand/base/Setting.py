import configparser
import json
import os

from .paras import SettingParas
from ...utils.base import ParkLY
from ...tools import (
    readPy,
    warning
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

    def open(self,
             path: str,
             **kwargs: dict
             ) -> object:
        """
        加载配置文件, 支持ini、json、py、txt
        :param path: 需要加载配置文件的路径
        :param kwargs:
        :return : 对象本身
        """
        if path:
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
