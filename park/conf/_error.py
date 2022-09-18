class UnknownError(Exception):
    """未知错误"""
    def __init__(self, *args, **kwargs):
        pass


class SettingError(BaseException):
    """配置错误"""
    def __init__(self, *args, **kwargs):
        pass


class DataError(ValueError):
    """数据错误"""
    def __init__(self, *args, **kwargs):
        pass


class SaveError(BaseException):
    """保存失败"""
    def __init__(self, *args, **kwargs):
        pass


class SQLError(BaseException):
    """sql错误"""
    def __init__(self, *args, **kwargs):
        pass


class DataPathError(DataError):
    """数据路径错误"""
    def __init__(self, *args, **kwargs):
        pass


class OrderError(SettingError):
    """指令错误"""
    def __init__(self, *args, **kwargs):
        pass


class NetworkError(SettingError):
    """神经网络错误"""
    def __init__(self, *args, **kwargs):
        pass


class LossError(SettingError):
    """损失函数错误"""
    def __init__(self, *args, **kwargs):
        pass


class ProjectError(ValueError):
    """项目错误"""
    def __init__(self, *args, **kwargs):
        pass


class EpochError(ValueError):
    """迭代错误"""
    def __init__(self, *args, **kwargs):
        pass


__all__ = (
    'UnknownError',
    'SettingError',
    'DataPathError',
    'DataError',
    'SaveError',
    'SQLError',
    'OrderError',
    'NetworkError',
    'LossError',
    'ProjectError',
    'EpochError',
)
