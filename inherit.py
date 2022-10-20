import json
import os
import copy
import warnings
import configparser


def _readPy(file):
    """
    file 为 字符串
    将py格式的字符串中的变量生成字典形式返回
    """
    exec(file)
    return locals()


def _setAttrs(self, **kwargs):
    """
    对传入的self 对象设置属性， 必须保证该对象有paras 属性，并且paras为SettingParas
    设置的属性为 _set_dict 中的字典数据  调用方式
    self.key = value
    """
    if hasattr(self, 'paras') and isinstance(self.paras, SettingParas):
        for key, value in self.paras._set_dict.items():
            if not hasattr(self, key):
                setattr(self, key, value)
            else:
                if self.paras._warn and self.paras._cover:
                    warnings.warn("当前设置重复的属性，将覆盖该属性", RuntimeWarning, stacklevel=2)
                if self.paras._cover:
                    setattr(self, key, value)
    elif kwargs:
        for key, value in kwargs.items():
            setattr(self, key, value)
    return self


class Paras:
    """
    配置基础类
    含有参数
    _allow 默认允许 设置属性
    _allow_set 表示允许随时修改属性 设置属性
    """
    _allow = False
    _allow_set = []

    def __init__(self, allow=True, **kwargs):
        """
        默认初始化时允许设置属性
        """
        self._allow = allow
        try:
            _setAttrs(self, **kwargs)
        except Exception as e:
            warnings.warn(f"属性设置失败 原因：{e}", RuntimeWarning, stacklevel=2)
        finally:
            self._allow = False

    @staticmethod
    def _get_cls_dir(self):
        """
        获取self对象包含的 方法
        """
        return dir(self)

    def __setattr__(self, key, value):
        if key not in self._allow_set + ['_allow'] and not self._allow:
            raise AttributeError('该类不允许设置属性')
        return super(Paras, self).__setattr__(key, value)


class SettingParas(Paras):
    """
    配置文件类
    默认包含
    _root  超级权限， 目前仅提供 查询 _{item} 的内置属性
    _warn  是否弹出警告 信息
    _cover 设置属性时是否覆盖
    _set_dict 设置属性的字典数据
    _suffix_ini 支持的config 文件中的后缀列表
    _suffix  文件后缀
    context  上下文信息， 默认字典形式
    """
    _allow_set = ['_set_dict', 'context', '_root', '_warn', '_cover']

    @staticmethod
    def init():
        _root = False
        _warn = False
        _cover = True
        _set_dict = {}
        _suffix_ini = ['.ini', '.cfg', '.conf']
        context = {}
        return locals()

    def __init__(self):
        super(SettingParas, self).__init__(allow=True, **self.init())


class Setting(object):

    def __init__(self):
        """
        定义 配置文件中的 基础设置
        """
        self.paras = SettingParas()

    def load(self, path: str, **kwargs):
        """加载配置文件, 支持ini、json、py、txt"""
        _, suffix = os.path.splitext(path)
        suffix = suffix.lower()
        if suffix == '.py':
            with open(path, 'r', encoding=kwargs.get("encoding", None)) as f:
                file = f.read()
                self.paras._set_dict = {**self.paras._set_dict, **_readPy(file)}
        elif suffix == '.json':
            with open(path, 'r', encoding=kwargs.get("encoding", None)) as f:
                self.paras._set_dict = {**self.paras._set_dict, **json.load(f)}
                f.close()
        elif suffix in self.paras._suffix_ini:
            config = configparser.ConfigParser()
            config.read(path, encoding='utf-8')
            d = {}
            for item in config:
                if config.has_section(item):
                    d[item] = dict(config.items(item))
            self.paras._set_dict = {**self.paras._set_dict, **d}
        elif suffix == 'txt':
            d = {}
            with open(path, 'r', encoding=kwargs.get("encoding", None)) as f:
                lines = f.readlines()
            for line in lines:
                try:
                    key, value = line.split("=")
                    d[key] = value
                except Exception as e:
                    print(f"({line})该行配置错误({e})")
                    continue
            self.paras._set_dict = {**self.paras._set_dict, **d}
        else:
            raise IOError(f"暂不支持该格式({suffix})配置文件")
        return _setAttrs(self=self)

    def __getattribute__(self, item):

        res = super(Setting, self).__getattribute__(item)
        if item.startswith("_") and not self.paras._root:
            if item in self.paras._get_cls_dir(Setting):
                if callable(res):
                    return res
            raise AttributeError("不允许获取私有属性")
        return res

    def sudo(self):
        return Setting().with_root(self)

    def with_root(self, obj):
        self.paras = copy.deepcopy(obj.paras)
        self.paras._root = True
        return _setAttrs(self)

    def with_context(self, context=None):
        obj = Setting()
        obj.paras = copy.deepcopy(self.paras)
        obj.paras.context = context
        return _setAttrs(obj)

    @property
    def context(self):
        return self.paras.context

    def save_setting(self):
        return self._args


if __name__ == "__main__":
    setting = Setting()
    setting.load(r'C:\Users\PC\Desktop\ParkTorch\config.json')
    # print(setting._args)
    print(setting.sudo()._args)
    print(setting._args)
