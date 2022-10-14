import re

from ._error import *


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


def exists_rename(path: str, paths: list = None) -> str:
    from .os import isType, listPath, dirName, base, join
    if isType(path=path, form='dir'):
        if path.endswith('/'):
            path = path[:-1]
        names = listPath(path=dirName(path), splicing=False, list=True)
        return join(dirName(path), _generate_name(name=base(path), names=names))
    if isType(path=path, form='doc'):
        names = listPath(path=dirName(path), splicing=False, list=True)
        return join(dirName(path), _generate_name(name=base(path), names=names, mode=1))
    else:
        names = []
        if paths:
            names = paths
        return _generate_name(name=path, names=names)


def _generate_name(name: str, names: list, mode=0) -> str:
    suffix = ''
    if mode == 1:
        from .os import splitPath, absPath
        name, suffix = splitPath(name)
        names = list(map(lambda x: splitPath(x)[0], filter(lambda x: splitPath(x)[1] == suffix, names)))
    if name in names:
        pattern = re.compile(r'.*\((\d+)\)')
        number = re.match(pattern=pattern, string=name)
        if number:
            number = number.group(1)
            new_name = re.sub(r'\(\d+\)$', '(%d)' % (int(number) + 1), name)
        else:
            new_name = name + ' (1)'
        if new_name in names:
            return _generate_name(new_name, names)
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
