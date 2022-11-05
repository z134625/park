import os
import logging
import shutil
from functools import reduce
from typing import Union
from collections.abc import Iterator


def _path_join(*args) -> str:
    """文件路径拼接"""
    return str(reduce(os.path.join, args))


def _is_file(path: str) -> bool:
    """判断是否为文件"""
    return os.path.isfile(path)


def _is_dir(path: str) -> bool:
    """判断是否为路径"""
    return os.path.isdir(path)


def _is_abs(path: str) -> bool:
    """判断是否为绝对路径"""
    return os.path.isabs(path)


def _is_type(path: str, **kwargs) -> bool:
    """
    :param path:
    :param kwargs:
    :return:
    """
    file = kwargs.get('form', "dir")
    warn = kwargs.get('warn', True)
    if _is_exists(path):
        if file == "doc" or file == "file":
            return _is_file(path)
        else:
            return _is_dir(path)
    else:
        if warn:
            logging.warning("(%s)该文件或路径不存在" % path)
        return False


def _path_abs(path: str) -> str:
    """返回路径绝对路径"""
    return os.path.abspath(path)


def _is_exists(path: str) -> bool:
    """判断是否存在"""
    if path:
        return os.path.exists(path)


def _mkdir_path(path: str, exist_ok: bool = True) -> None:
    """创建文件夹"""
    dir_ = path
    try:
        os.mkdir(dir_)
    except FileExistsError:
        return
    except FileNotFoundError:
        os.makedirs(dir_, exist_ok)
    finally:
        return


def _list_path(path: str, **kwargs) -> Iterator:
    """
    列出路径下的所有文件
    :param path: 路径
    :param kwargs: 支持使用where进行条件筛选， where 传入参数应为一种函数或者方法，需要的则应返回True， 不需要的返回False
    :return : 一组文件名
    """
    doc = kwargs.get("doc", False)
    doc_ = kwargs.get("file", False)
    dir_ = kwargs.get("dir", False)
    like = kwargs.get("like", None)
    list_ = kwargs.get("list", True)
    splicing = kwargs.get("splicing", False)
    assert (doc and not dir_) or (not doc and dir_) or (not doc and not dir_),\
        "file and dirs is conflicted (file 和 dirs不能同时使用)"
    
    files = os.listdir(absPath(path))
    if doc or doc_:
        files = filter(lambda x: _is_file(join(path, x)), files)
    if dir_:
        files = filter(lambda x: _is_dir(join(path, x)), files)
    if like:
        files = filter(lambda x: like in x, files)
    if splicing:
        files = map(lambda x: join(path, x), files)
    if list_:
        files = list(files)
    return files


def _env_path(key, value) -> None:
    """
    系统变量配置
    :param key: 设置变量名
    :param value:  变量值
    :return: 不返回内容
    """
    os.environ[key] = value
    return


def _base_name(path: str) -> str:
    """获取文件名"""
    return os.path.basename(path)


def _dir_name(path: str) -> str:
    """获取路径"""
    return os.path.dirname(path)


def _remove(path: str) -> bool:
    """删除文件"""
    try:
        os.remove(path)
        return True
    except PermissionError:
        shutil.rmtree(path)
        return True
    except FileNotFoundError:
        print(f"\033[0;31;31m该文件或文件夹({path})不存在或已删除\033[0m")
        return False


def _split_path(path: str) -> tuple:
    """分割文件名和后缀"""
    return os.path.splitext(path)


def _get_size(path: str) -> Union[int, str]:
    """获取文件大小"""
    if path:
        return os.path.getsize(path)
    else:
        return "0"


def _get_base_path(is_abs: bool = False) -> str:
    """
    获取当前工作路径
    :param is_abs: 默认为否， 开启则返回工作路径的绝对路径
    :return:  返回路径字符串
    """
    if is_abs:
        return _path_abs(os.getcwd())
    return os.getcwd()


BASE_PATH = _get_base_path()
join = _path_join
isType = _is_type
isAbs = _is_abs
absPath = _path_abs
isExists = _is_exists
mkdir = _mkdir_path
listPath = _list_path
env = _env_path
base = _base_name
dirName = _dir_name
remove = _remove
splitPath = _split_path
getSize = _get_size


