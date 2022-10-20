import re
from collections.abc import Iterable

from ._error import *
from .os import splitPath, absPath


__all__ = ("Error", "exists_rename")
__doc__ = """    'BASE_PATH': 当前工作路径
    'Time': 现在时间格式xxxx-xx-xx : xx:xx:xx xx
    'Date',  现在时间格式 xxxx-xx-xx
    'Stamp',  现在时间戳
    'Command', : 终端输入代码指令
    'setting',  : 配置文件支持加载json,py,ini,txt 格式配置文件 使用方法: setting.load(filename)
    'RecordingMode',  : 日志记录采用的时间格式， 通过配置文件note_time=True(NOW)修改
    'Error', : 错误类
    'ProgressPark', : 进度条工具 使用方法 with ProgressPark(len(item)) as park:
                                            for i in item:
                                                park()
    'join', : 文件路径拼接， 支持多个路径拼接
    'isFile', : 判断是否为文件
    'isDir', : 判断是否为路径
    'isAbs', : 判断是否为绝对路径
    'absPath', : 返回绝对路径
    'isExists', : 判断是否为存在
    'mkdir', : 创建文件夹可存在则不创建
    'listPath', : 列车提供路径中所有文件
    'env', : 修改系统环境
    'base', : 返回文件名
    'remove', : 删除文件或文件夹，
    'splitPath', 分割路径和文件
    'getSize',  获取文件大小
"""


class _ErrorClass:
    """数据处理错误文件删除工具"""

    def __init__(self, file_path: str = None, delete: bool = False, fileName: str = None):
        from .os import join, BASE_PATH, remove
        if file_path:
            path = file_path
        else:
            path = join(BASE_PATH, 'cache/error')
        if delete:
            if fileName:
                remove(join(path, fileName))
            else:
                remove(path)

    @staticmethod
    def UnknownError(msg: str) -> UnknownError:
        return UnknownError(msg)

    @staticmethod
    def SettingError(msg: str) -> SettingError:
        return SettingError(msg)

    @staticmethod
    def DataPathError(msg: str) -> DataPathError:
        return DataPathError(msg)

    @staticmethod
    def DataError(msg: str) -> DataError:
        return DataError(msg)

    @staticmethod
    def SaveError(msg: str) -> SaveError:
        return SaveError(msg)

    @staticmethod
    def SQLError(msg: str) -> SQLError:
        return SQLError(msg)

    @staticmethod
    def OrderError(msg: str) -> OrderError:
        return OrderError(msg)

    @staticmethod
    def NetworkError(msg: str) -> NetworkError:
        return NetworkError(msg)

    @staticmethod
    def LossError(msg: str) -> LossError:
        return LossError(msg)

    @staticmethod
    def ProjectError(msg: str) -> ProjectError:
        return ProjectError(msg)

    @staticmethod
    def EpochError(msg: str) -> EpochError:
        return EpochError(msg)


def exists_rename(path: str, paths: list = None,
                  warn: bool = False,
                  clear: bool = False,
                  dif: bool = False) -> str:
    from .os import isType, listPath, dirName, base, join
    if not clear:
        if isType(path=path, form='dir', warn=warn):
            if path.endswith('/'):
                path = path[:-1]
            names = listPath(path=dirName(path), splicing=False, list=True)
            return join(dirName(path), _generate_name(name=base(path), names=names, dif=dif))
        if isType(path=path, form='doc', warn=warn):
            names = listPath(path=dirName(path), splicing=False, list=True)
            return join(dirName(path), _generate_name(name=base(path), names=names, mode=1, dif=dif))
        else:
            names = []
            if paths:
                names = paths
            return _generate_name(name=path, names=names, dif=dif)
    else:
        name, suffix = splitPath(path)
        pattern = re.compile(r'(.*) \([0-9]+\)')
        res = re.search(pattern=pattern, string=name)
        if res:
            name_head = res.group(1)
            return name_head + suffix
        else:
            return path


def _generate_name(name: str, names: Iterable[str], mode=0, dif=False) -> str:
    suffix = ''
    if mode == 1:
        name, suffix = splitPath(name)
        names = list(map(lambda x: splitPath(x)[0], filter(lambda x: splitPath(x)[1] == suffix, names)))
    if name in names:
        start = ' (1)'
        pattern_number = re.compile(r'.* \((\d+)\)')
        pattern_letter = re.compile(r'.* \(([A-Z]+)\)')
        pattern = pattern_number
        if dif:
            start = ' (A)'
            pattern = pattern_letter
        number = re.match(pattern=pattern, string=name)
        if number:
            number = number.group(1)
            if not dif:
                new_name = re.sub(r'\(\d+\)$', '(%d)' % (int(number) + 1), name)
            else:
                if not number.endswith('Z'):
                    new_name = re.sub(r'\([A-Z]+\)$', '(%s)' % (number[:-1] + chr(ord(number[-1]) + 1)), name)
                else:
                    new_name = re.sub(r'\([A-Z]+\)$', '(%s)' % (number + 'A'), name)
        else:
            new_name = name + start
        if new_name in names:
            return _generate_name(new_name, names, mode=0, dif=dif)
        return new_name + suffix
    return name + suffix


Error = _ErrorClass

del _ErrorClass,\
    UnknownError,\
    SettingError,\
    DataError, \
    SaveError,\
    SQLError, \
    DataPathError,\
    NetworkError, \
    OrderError,\
    LossError, \
    ProjectError,\
    EpochError
