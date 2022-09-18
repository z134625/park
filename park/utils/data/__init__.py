"""
数据类封装数据信息
"""
import os
from typing import Union, Any
ndarray = __import__("numpy").ndarray

__all__ = (
    "SettingData",
    "formatSize",
    "DataInfo",
    "CoilData",
    "Normalization",
    "Compare",
    "VersionCompare",
    "RequestInfo",
    "RenderData"
)


class _SettingAttribute:
    """
    配置文件中数据
    优化其数据可以通过实例化配置数据得到数据一些信息
    也可调用一些方法将得到的配置文件数据转化为浮点数，整数，
    data.value: 将返回配置文件真实值，大多数配置文件读取都是字符串类型，json除外
    data.int: 将得到数据的整型若该数据不支持，将报错，原型即int(data)
    data.float: 将得到数据的浮点型若该数据不支持，将报错，原型即float(data)
    data.tree: 得到数据树，例
    config.ini中存在数据:
    [default]
    data = 1
    那么
    >> setting.data.tree
    out: (default)->(data)->(1)
    """

    def __init__(self, key: Union[list, str, tuple], value: Any):
        self.key: str = key
        self._value: Any = value

    def __str__(self) -> str:
        return str(self._value)

    @property
    def value(self) -> Any:
        return self._value

    @property
    def float(self) -> float:
        return float(self._value)

    @property
    def int(self) -> int:
        return int(self._value)

    @property
    def list(self) -> list:
        return list(eval(str(self._value)))

    @property
    def tuple(self) -> tuple:
        return tuple(eval(str(self._value)))

    @property
    def dict(self) -> dict:
        return dict(eval(str(self._value)))

    @property
    def set(self) -> set:
        return set(eval(str(self._value)))

    def __getattr__(self, item):
        if item == 'tree':
            if isinstance(self.key, str):
                return f'({self.key})->({self._value})'
            elif isinstance(self.key, list) or isinstance(self.key, tuple):
                res = [f'({i})' for i in self.key]
                res = '->'.join(res)
                return res + f'->({self._value})'
        return None


class _DataInfo:
    def __init__(self, data: Any, file: str = None):
        self.data = data
        self.file = file
        if not isinstance(self.data, ndarray):
            np = __import__("numpy")
            self.data = np.array(self.data)

    @property
    def size(self) -> Union[None, str]:
        if self.file:
            return _formatSize(os.path.getsize(self.file))
        return None

    @property
    def name(self) -> Union[None, str]:
        if self.file:
            return os.path.basename(self.file)
        return None

    @property
    def shape(self) -> tuple:
        return self.data.shape

    @property
    def np(self) -> ndarray:
        return self.data

    @property
    def tensor(self) -> Any:
        torch = __import__("torch")
        return torch.from_numpy(self.data)


class _CoilData:
    __slots__ = ["files", "file_dir", "t", "c"]

    def __init__(self, file_dir: str):
        if not os.path.isdir(file_dir):
            raise ValueError("必须传入数据路径，不能传入文件路径")
        self.file_dir = os.path.abspath(file_dir)
        c, t = os.path.split(self.file_dir)
        self.t = t
        _, self.c = os.path.split(c)
        self.files = []
        for file in os.listdir(file_dir):
            self.files.append(os.path.join(file_dir, file))

    def __getitem__(self, item):
        if isinstance(item, int):
            return self.files[item]
        elif isinstance(item, str):
            return list(filter(lambda x: item in x, self.files))
        else:
            raise ValueError("不支持此方式(%s)查找该对象" % type(item))

    @property
    def time(self) -> str:
        return self.t

    @property
    def class_(self) -> str:
        return self.c

    @property
    def values(self) -> list:
        return self.files


class _VersionCompare:
    initial = None

    def __init__(self, version: str):
        self.initial = version
        self.initial_list = version.split('.')
        self.initial_list = list(map(lambda x: int(x), self.initial_list))

    def __eq__(self, other):
        return self._compare(other, "==")

    def __ne__(self, other):
        return self._compare(other, "!=")

    def __gt__(self, other):
        return self._compare(other, ">")

    def __ge__(self, other):
        return self._compare(other, ">=")

    def __lt__(self, other):
        return self._compare(other, "<")

    def __le__(self, other):
        return self._compare(other, "<=")

    def __bool__(self):
        return True

    def __str__(self):
        return self.initial

    def _compare(self, other: Any, mark: str) -> bool:
        if isinstance(other, self.__class__) and "initial" in dir(other):
            if self.initial_list.__len__() == other.initial_list.__len__():
                for x1, x2 in zip(self.initial_list, other.initial_list):
                    try:
                        x1, x2 = int(x1), int(x2)
                    except ValueError:
                        raise ValueError("不支持比较该版本类型")
                    if not x1 == x2:
                        return eval("x1 %s x2" % mark)
                return True
            else:
                raise ValueError("两个数据版本格式不对应不支持比较")
        else:
            raise ValueError("不支持非VersionCompare类进行比较")


def _formatSize(bytes_: Union[float, int]):
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


def _Compare(item1: Any, item2: Any) -> list:
    """
    比较两对象关系
    若无法比较，将返回一个空的列表
    只要符合比较的要求，符号都会返回到列表中
    _Compare(1, 1)
    ["=", ">=", "<="]
    _Compare(1, 2)
    ["<=", "<"]
    _Compare(3, 1)
    [">=", ">"]
    """
    res = []
    if item1 == item2:
        res.append("=")
    if item1 >= item2:
        res.append(">=")
    if item1 <= item2:
        res.append("<=")
    if item1 > item2:
        res.append(">")
    if item1 < item2:
        res.append("<")
    return res


class _Normalization:
    """
    数据预处理，
    本方法将数据归一化处理提供数据归一化，数据还原功能
    初始化定义归一化数据的范围
    fit_data 将返回数据经过归一化后的数据且数据导入和返回都为numpy形式
    使用算法为 (x - x_min) / (x_max - x_min) * (max - min) + min
    reduction_data 将还原数据
    使用逆向算法
    默认数据范围为-1, 1传入元组数据 也可列表，
    Example :

    normal = _Normalization()
    a = normal.fit_data(np.arange(1, 10))
    a
    array([-1.  , -0.75, -0.5 , -0.25,  0.  ,  0.25,  0.5 ,  0.75,  1.  ])
    normal.reduction_data(a)
    array([1., 2., 3., 4., 5., 6., 7., 8., 9.])
    """
    max_dif = 1
    max_data = 1
    min_data = 1

    def __init__(self, range_max_min: Union[tuple, None] = (1, -1)):
        if range_max_min \
                and isinstance(range_max_min, tuple)\
                and range_max_min.__len__() == 2:
            self.min_ = min(range_max_min)
            self.max_ = max(range_max_min)
        else:
            self.min_ = None
            self.max_ = None

    def fit_data(self, data: ndarray) -> ndarray:
        if self.max_ is not None and self.min_ is not None:
            self.max_data = max(data)
            self.min_data = min(data)
            self.max_dif = (self.max_data - self.min_data)
            return (data - self.min_data) / self.max_dif * (self.max_ - self.min_) + self.min_
        else:
            return data

    def reduction_data(self, data: ndarray) -> ndarray:
        if self.max_ is not None and self.min_ is not None:
            primary = (data - self.min_) / (self.max_ - self.min_)
            primary = primary * self.max_dif + self.min_data
            return primary
        else:
            return data


class _RequestInfo:
    def __init__(self, environ):
        self._request = environ

    def __getitem__(self, item):
        return self._request[item]

    def __getattr__(self, item):
        return self._request[item]


class RenderData:
    def __init__(self, html: str, status: int):
        self.html = html
        self.status = status


def _test():
    """
    >>> _formatSize(1024)
    '1.000KB'
    >>> _formatSize(1024 * 1024)
    '1.000M'
    >>> _formatSize(1000)
    '0.977KB'
    >>> _formatSize("fs")
    传入的字节格式不对
    'Error'
    >>> _Compare(1, 1)
    ['=', '>=', '<=']
    >>> _Compare(1, 2)
    ['<=', '<']
    >>> _Compare(3, 1)
    ['>=', '>']
    >>> normal = _Normalization()
    >>> a = normal.fit_data(np.arange(1, 10))
    >>> a
    array([-1.  , -0.75, -0.5 , -0.25,  0.  ,  0.25,  0.5 ,  0.75,  1.  ])
    >>> normal.reduction_data(a)
    array([1., 2., 3., 4., 5., 6., 7., 8., 9.])
    """


SettingData = _SettingAttribute
formatSize = _formatSize
DataInfo = _DataInfo
CoilData = _CoilData
Normalization = _Normalization
Compare = _Compare
VersionCompare = _VersionCompare
RequestInfo = _RequestInfo


if __name__ == '__main__':
    import doctest
    doctest.testmod()
