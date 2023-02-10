from typing import Tuple

from ....tools import _Context
from ....utils.paras import Paras


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
    ban = ['_suffix_ini', 'root_func']

    @staticmethod
    def init() -> dict:
        """
        设置基础配置
        """
        _error: bool = False
        _suffix_ini: Tuple[str, str, str] = ('.ini', '.cfg', '.conf')
        _setting = _Context({})
        return locals()
