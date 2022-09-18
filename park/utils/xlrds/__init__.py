import warnings
from collections.abc import Iterable
from typing import Any, Union
from ...conf.setting import install_module

if __name__ == "park.utils.xlrds":
    if install_module("xlrd", "xlrd==1.2.0") != 0:
        raise SystemError("模块xlrd下载失败")
    if install_module("xlwt", "xlwt~=1.3.0") != 0:
        raise SystemError("模块xlwt下载失败")

from .tools import (
    _open_excel,
    _create_workbook,
    _sheets,
    _list_sheet,
    _choice_sheet,
    _get_rows_cols,
    _get_row_values,
    _get_cell_value,
    _write_sheet,
    _save_excel,
    _add_sheet,
)


class ExcelOpen:
    """
    excel 操作类
    用于查看excel表格， 修改， 新建表格
    实例:
    excel = ExcelOpen(path="./test.xls", mode="r")

    """
    row_sheet = None

    def __init__(self, path: str, mode: str = "r"):
        self.path = path
        if "xlsx" in self.path:
            warnings.warn("该方法不支持操作xlsx文件，可能会有未知错误", RuntimeWarning, stacklevel=2)
        self.mode = mode
        if mode == 'r':
            self.workbook = _open_excel(self.path)
        elif mode == 'w':
            self.write_row = 0
            self.workbook = _create_workbook()
        elif mode == 'a':
            self.workbook = _create_workbook()
        else:
            raise ValueError("mode错误，不支持此操作形式(%s)" % mode)

    @property
    def sheets(self) -> list:
        if self.mode == "r":
            return _list_sheet(self.workbook)
        else:
            raise IOError("%s, 不支持查找此属性" % self.mode)

    def __getitem__(self, item):
        return self.Table(_choice_sheet(self.workbook, index=item))

    class Table:
        def __init__(self, table: Any):
            self.table = table
            self._shape = _get_rows_cols(self.table)

        @property
        def shape(self):
            return self._shape

        @property
        def rows(self):
            return self._shape[0]

        @property
        def cols(self):
            return self._shape[1]

        def __getitem__(self, item):
            if isinstance(item, tuple) and item.__len__() == 2:
                return _get_cell_value(self.table, *item)
            elif isinstance(item, int):
                return _get_row_values(self.table, item)
            else:
                raise ValueError("不支持此操作")

    def write_rows(self, item: Any, sheet: str, is_row: bool = False, row: int = None, column: int = None) -> None:
        if self.mode == 'w':
            table = self.__create_sheet(sheet)
            if not isinstance(item, Iterable):
                assert row, "传入单个值，必须传入写入行"
                assert column, "传入单个值，必须传入写入列"
                _write_sheet(table, row=row, column=column, info=item)
            else:
                if is_row:
                    for i, data in enumerate(item):
                        _write_sheet(table, self.write_row, i, info=data)
                else:
                    for i, data in enumerate(item):
                        _write_sheet(table, i, self.write_row, info=data)
                self.write_row += 1
        else:
            raise IOError("%s, 不支持写入操作" % self.mode)

    def write_dicts(self, item: dict, heard: list = None):
        for key in item:
            table = _add_sheet(self.workbook, key)
            row_number = 0
            if heard:
                row_number = 1
                for n, value in enumerate(heard):
                    _write_sheet(table, row=0, column=n, info=value)
            if not isinstance(item[key], Iterable):
                _write_sheet(table, row=0, column=0, info=item[key])
            elif isinstance(item[key], dict):
                dict_ = item[key]
                for key_1 in dict_:
                    _write_sheet(table, row=row_number, column=0, info=key_1)
                    row_number += 1
                    if isinstance(dict_[key_1], list) or isinstance(dict_[key_1], tuple):
                        for j, value in enumerate(dict_[key_1]):
                            _write_sheet(table, row=row_number, column=j, info=value)
                    elif isinstance(dict_[key_1], dict):
                        for key_2 in dict_[key_1]:
                            _write_sheet(table, row=row_number, column=0, info=key_2)
                            if isinstance(dict_[key_1][key_2], list) or isinstance(dict_[key_1][key_2], tuple):
                                for j, value in enumerate(dict_[key_1][key_2]):
                                    _write_sheet(table, row=row_number, column=j + 1, info=value)
                            row_number += 1

            else:
                for i, data in enumerate(item[key]):
                    _write_sheet(table, row=0, column=i, info=data)

    def __create_sheet(self, sheet):
        table = None
        try:
            table = _add_sheet(self.workbook, name=sheet)
            self.row_sheet = table
        except Exception:
            table = self.row_sheet
        finally:
            return table

    def write_dict(self, item: dict, heard: list = None, table: Any = None, name: str = "sheet") -> None:
        if not table:
            table = _add_sheet(self.workbook, name)
        if heard and set(heard) == set(item.keys()):
            for i, key in enumerate(heard):
                values = item[key]
                self.__dict_func(table, values, i, key)
        else:
            for i, (key, values) in enumerate(item.items()):
                self.__dict_func(table, values, i, key)

    @staticmethod
    def __dict_func(table: Any, values: Any, i: int, key: Union[str, int]):
        if isinstance(values, Iterable) and not isinstance(values, str):
            _write_sheet(table=table, row=0, column=i, info=key)
            for j, val in enumerate(values):
                _write_sheet(table=table, row=j + 1, column=i, info=val)
        else:
            _write_sheet(table=table, row=0, column=i, info=key)
            _write_sheet(table=table, row=1, column=i, info=values)

    def save(self) -> None:
        if self.mode == "w":
            _save_excel(self.workbook, path=self.path)
        else:
            raise IOError("%s, 不支持保存操作" % self.mode)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.mode == 'w':
            self.save()
