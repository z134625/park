import numpy as np

from typing import Union, Any
from numpy import ndarray


__all__ = (
    'array_data',
    'asarray_data',
    'Ndarray',
    'range_data',
    'one_data',
    'zeros_data',
    'full_data',
    'diag_data',
    'eye_data',
    'inspace_data',
    'log_data',
    'sum_data',
    'reshape_data',
    'slice_data',
    'T_data',
    'isnan',
    'random_choice',
    'random_shuffle',
    'concatenate',
    'mean',
    'zeros_like',
    'dstack',
    'add_row',
    'add_column',
)

Ndarray = ndarray


def array_data(data: Union[list, tuple, Any], *args, **kwargs) -> Ndarray:
    """
    :param data: 数组
    :return:  返回ndarray数组
    用于将数组转换为numpy类型
    """
    return np.array(data, *args, **kwargs)


def asarray_data(data: Union[list, tuple, Any], *args, **kwargs) -> Ndarray:
    """
    :param data: 数组
    :return:  返回ndarray数组
    用于将数组转换为numpy类型
    而data若为numpy类型， 当data改变时该方法得到的numpy数据也会改变
    """
    return np.array(data, *args, **kwargs)


def range_data(n: int, *args, **kwargs) -> Ndarray:
    """
    :param n:  数组
    :return: 返回ndarray数组
    得到一个range(n) 的numpy数据
    即 np.array(range(n))
    """
    return np.arange(n, *args, **kwargs)


def one_data(shape: tuple, *args, **kwargs) -> Ndarray:
    """
    :param shape: 数组形状
    :return: 返回ndarray数组
    得到一个与shape形状一致的元素为1. 的数组
    type默认为float64
    可增加dtype = "int32" 修改
    """
    return np.ones(shape, *args, **kwargs)


def zeros_data(shape: tuple, *args, **kwargs) -> Ndarray:
    """
    :param shape: 数组形状
    :return: 返回ndarray数组
       得到一个与shape形状一致的元素为0. 的数组
    type默认为float64
    可增加dtype = "int32" 修改
    """
    return np.zeros(shape, *args, **kwargs)


def full_data(shape: tuple, val: Union[int, float], *args, **kwargs) -> Ndarray:
    """
    :param shape: 数组形状
    :param val: 数组值
    :return: 返回ndarray数组
    """
    return np.full(shape, val, *args, **kwargs)


def diag_data(v: Union[int, float], k: Union[int, float] = 0, *args, **kwargs) -> Ndarray:
    """
    :param v: 对角元素
    :param k: 其余元素
    :return: 返回ndarray数组
    """
    return np.diag(v, k, *args, **kwargs)


def eye_data(n: int, *args, **kwargs) -> Ndarray:
    """
    :param n:
    :return: 返回ndarray数组
    """
    return np.eye(n, *args, **kwargs)


def inspace_data(start: Union[int, float], stop: Union[int, float], num: int = 50, *args, **kwargs) -> Ndarray:
    """
    :param start:
    :param stop:
    :param num:
    :return: 返回ndarray数组
    """
    return np.linspace(start, stop, num, *args, **kwargs)


def log_data(start: Union[int, float], stop: Union[int, float], num: int = 50, *args, **kwargs) -> Ndarray:
    """
    :param start:
    :param stop:
    :param num:
    :return: 返回ndarray数组
    """
    return np.logspace(start, stop, num, *args, **kwargs)


def sum_data(array: Ndarray, *args, **kwargs) -> Ndarray:
    """
    :param array:
    :return:
    """
    return np.sum(array, *args, **kwargs)


def reshape_data(data: Ndarray, *args) -> Ndarray:
    """
    :param data: 需要整型的数据
    :return:
    """
    return data.reshape(*args)


def slice_data(data: Ndarray) -> Ndarray:
    """
    :param data:
    :return:
    """
    return data[:]


def T_data(data: Ndarray) -> Ndarray:
    """
    :param data:
    :return:
    """
    return data.T


def isnan(data: Ndarray) -> Ndarray:
    """
    :param data:
    :return:
    """
    return np.isnan(data)


def random_choice(data: Ndarray, num: int) -> Ndarray:
    """
    """
    return data[np.random.randint(data.shape[0], size=num)]


def random_shuffle(data: Ndarray) -> None:
    """
    """
    np.random.shuffle(data)
    return


def concatenate(data1: Ndarray, data2: Union[Ndarray, None] = None) -> Ndarray:
    """
    """
    if data2 is None:
        return data1
    elif data1 is None and data2 is not None:
        return data2
    else:
        return np.concatenate((data1, data2))


def mean(data: Any, **kwargs) -> Ndarray:
    """
    """
    return np.mean(data, **kwargs)


def zeros_like(data: Ndarray, **kwargs) -> Ndarray:
    """
    """
    return np.zeros_like(data, **kwargs)


def dstack(data: tuple, **kwargs) -> Ndarray:
    """
    """
    return np.dstack(data, **kwargs)


def add_row(data: Ndarray, row: Any, after: bool = True) -> Ndarray:
    """
    """
    assert isinstance(row, list) or isinstance(row, Ndarray), "增加的行必须是列表形式或者numpy数据类型"
    if isinstance(row, list):
        row = array_data(row)
    if after:
        return np.row_stack((data, row))
    else:
        return np.row_stack((row, data))


def add_column(data: Ndarray, row: Any, after: bool = True) -> Ndarray:
    """
    """
    assert isinstance(row, list) or isinstance(row, Ndarray), "增加的行必须是列表形式或者numpy数据类型"
    if isinstance(row, list):
        row = array_data(row)
    if after:
        return np.column_stack((data, row))
    else:
        return np.column_stack((row, data))


