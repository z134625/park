import os
import shutil
import sys
import warnings
import logging

from typing import Union, List, Any

LISTFILE = 0
LISTDIR = 1
LISTALL = 2


def warning(msg: str, warn: bool = True,
            types: warnings = RuntimeWarning,
            stacklevel: int = 2) -> None:
    """
    警告方法，
    """
    if warn:
        warnings.warn(msg, types, stacklevel=stacklevel)
    return


def mkdir(path: str, exist: bool = True) -> bool:
    """
    创建文件夹
    """
    dir_: str = path
    try:
        os.mkdir(dir_)
    except FileExistsError:
        return False
    except FileNotFoundError:
        os.makedirs(dir_, exist)
    finally:
        return True


def remove(path: str, warn=True) -> bool:
    """删除文件"""
    try:
        os.remove(path)
        return True
    except PermissionError:
        shutil.rmtree(path)
        return True
    except FileNotFoundError:
        warning(f"该文件或文件夹({path})不存在或已删除", warn=warn)
        return False


def listPath(path: str, mode: int = LISTFILE, **kwargs) -> Union[list, map, filter]:
    """
    列出路径下的所有文件
    :param path: 路径
    :param mode: 模式
    :param kwargs: 支持使用where进行条件筛选， where 传入参数应为一种函数或者方法，需要的则应返回True， 不需要的返回False
    :return : 一组文件名
    """
    doc: bool = False
    dir_: bool = False
    if mode == 0:
        doc: bool = True
    elif mode == 1:
        dir_: bool = True
    like: str = kwargs.get("like", None)
    list_: bool = kwargs.get("list", True)
    splicing: bool = kwargs.get("splicing", False)
    files: List[str] = list(filter(lambda x: not x.startswith('.'), os.listdir(path)))
    if doc:
        files: filter = filter(lambda x: os.path.isfile(os.path.join(path, x)), files)
    if dir_:
        files: filter = filter(lambda x: os.path.isdir(os.path.join(path, x)) if not x.startswith('.') else False,
                               files)
    if like:
        files: filter = filter(lambda x: like in x, files)
    if splicing:
        files: map = map(lambda x: os.path.join(path, x), files)
    if list_:
        files: List[str] = list(files)
    return files


def formatSize(bytes_: Union[float, int]):
    """
    :param bytes_: 数据字节数
    :return:  返回数据字节转化大小， kb, M, G
    _formatSize(1024)
    '1.000KB'
    _formatSize(1024 * 1024)
    '1.000M'
    _formatSize(1000)
    '0.977KB'
    _formatSize("fs")
    传入的字节格式不对
    'Error'
    """
    try:
        bytes_ = float(bytes_)
        kb = bytes_ / 1024
    except ValueError:
        print("传入的字节格式不对")
        return "Error"

    if kb >= 1024:
        M = kb / 1024
        if M >= 1024:
            G = M / 1024
            return "%.3fG" % G
        else:
            return "%.3fM" % M
    else:
        return "%.3fKB" % kb


def get_size(item):
    def _get_size(obj, seen=None):
        size = sys.getsizeof(obj)
        if seen is None:
            seen = set()
        obj_id = id(obj)
        if obj_id in seen:
            return 0
        seen.add(obj_id)
        if isinstance(obj, dict):
            size += sum([_get_size(v, seen) for v in obj.values()])
            size += sum([_get_size(k, seen) for k in obj.keys()])
        elif hasattr(obj, '__dict__'):
            size += _get_size(obj.__dict__, seen)
        elif hasattr(obj, '__iter__') and not isinstance(obj, (str, bytes, bytearray)):
            size += sum([_get_size(i, seen) for i in obj])
        return size

    return formatSize(_get_size(item))


def readPy(file: str) -> dict:
    """
    file 为 字符串
    将py格式的字符串中的变量生成字典形式返回
    """
    exec(file)
    return locals()


def setAttrs(obj: Any, self: bool = False, cover: bool = True, warn: bool = True, **kwargs) -> Any:
    """
    对传入的obj 对象设置属性， 必须保证该对象有paras 属性，并且paras为Paras
    对于有paras 属性的 对象， 可在paras 设置属性 _cover 以及 _warn 来限制是否弹出警告 是否覆盖属性内容
    对于非paras 的对象 可在添加参数cover warn 默认都为True 设置的属性 增加函数参数即可
    即： setAttrs(obj, _cover=True, _warn=False
    对应的 这将对obj 对象设置 _cover _warn 两个参数
    设置的属性为 _set_dict 中的字典数据  调用方式
    obj.key = value
    self 参数在复制一个对象时， 会重复设置属性此时 为True避免重复警告  默认为False
    """
    if hasattr(obj, 'paras') and hasattr(obj.paras, '_park_paras') and getattr(obj.paras, '_park_paras'):
        cover: bool = True
        warn: bool = True
        for key, value in obj.paras._set_list:
            root = obj.paras._root
            if not root:
                obj.paras._root = True
            has: bool = key in dir(obj)
            if not root:
                obj.paras._root = False
            if not has:
                setattr(obj, key, value)
            else:
                warning("当前设置重复的属性(%s)，将覆盖该属性" % key,
                        warn=(warn and obj.paras._warn) and (cover and obj.paras._cover) and not self)
                if cover and obj.paras._cover:
                    setattr(obj, key, value)
            if obj.paras._root:
                d: dict = {
                    key: eval(f'obj.{key}')
                }
            else:
                obj.paras._root = True
                d: dict = {
                    key: eval(f'obj.{key}')
                }
                obj.paras._root = False
            obj.paras._attrs.update(d)
        obj.paras._set_list.clear()
    elif kwargs:
        for key, value in kwargs.items():
            warning("当前设置重复的属性(%s)，将覆盖该属性" % key, warn=warn and cover)
            if cover:
                setattr(obj, key, value)
    return obj


class _Context(dict):

    def __getattribute__(self, item):
        try:
            return super().__getattribute__(item)
        except AttributeError:
            return self.__getattr__(item)

    def __getattr__(self, item):
        if item in self:
            return self[item]
        raise AttributeError(f'属性错误, 没有该属性{item}')

