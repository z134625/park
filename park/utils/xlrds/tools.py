import os.path
import openpyxl

from typing import Any, Union, List, Tuple
from collections.abc import Iterable
from ...conf.os import mkdir
from ...conf.setting import make_dir_or_doc


xlrd = __import__("xlrd")
xlwt = __import__("xlwt")


def _open_excel(path: str) -> xlrd.book.Book:
    """
    打开一个excel文件
    :param path: excel文件路径
    :return: 一个工作簿
    """
    workbook = xlrd.open_workbook(r"%s" % path)
    return workbook


def _list_sheet(workbook: xlrd.book.Book) -> list:
    """
    获取excel中的sheet表列表
    :param workbook: 工作簿
    :return: 一个列表sheet名
    """
    assert isinstance(workbook, xlrd.book.Book), "必须传入xlrd读取的工作薄"
    return workbook.sheet_names()


def _sheets(workbook: xlrd.book.Book) -> Any:
    """

    :param workbook:
    :return:
    """
    assert isinstance(workbook, xlrd.book.Book), "必须传入xlrd读取的工作薄"
    return workbook.sheets()


def _choice_sheet(workbook: xlrd.book.Book,
                  index: Union[str, int, List[int], Tuple[int]]) -> \
        Union[xlrd.sheet.Sheet, map]:
    assert isinstance(workbook, xlrd.book.Book), "必须传入xlrd读取的工作薄"
    if isinstance(index, int):
        return workbook.sheet_by_index(index)
    elif isinstance(index, str):
        return workbook.sheet_by_name(index)
    elif isinstance(index, Iterable) and index:
        return map(lambda x: workbook.sheet_by_index(x) if isinstance(x, int) else workbook.sheet_by_name(x),
                   index)
    else:
        raise ValueError("不支持此数据类型")


def _get_rows_cols(table: xlrd.sheet.Sheet) -> Tuple[Any, Any]:
    rows = table.nrows
    cols = table.ncols
    return rows, cols


def _get_row_values(table: xlrd.sheet.Sheet, row: int) -> List[str]:
    if isinstance(row, int):
        return table.row_values(row)
    elif isinstance(row, slice):
        return table.row_slice(row)
    else:
        raise ValueError("传入数据错误")


def _get_cell_value(table: xlrd.sheet.Sheet, row: int, column: int) -> str:
    return table.cell(row, column).value


def _create_workbook():
    return xlwt.Workbook()


def _add_sheet(workbook: xlwt.Workbook, name: str) -> xlwt.Worksheet:
    if name.__len__() > 31:
        name = name[:31]
    return workbook.add_sheet(r"%s" % name, cell_overwrite_ok=True)


def _write_sheet(table: xlwt.Worksheet, row: int, column: int, info: str) -> Any:
    return table.write(row, column, info)


def _save_excel(workbook: xlwt.Workbook, path: str) -> None:
    make_dir_or_doc(path, suffix='xls')
    f = open(path, 'w')
    f.close()
    workbook.save(path)


def _open_a_excel(path: str, *args, **kwargs):
    return openpyxl.open(path, *args, **kwargs)


open_excel = _open_excel
create_workbook = _create_workbook
sheets = _sheets
list_sheet = _list_sheet
choice_sheet = _choice_sheet
get_rows_cols = _get_rows_cols
get_row_values = _get_row_values
get_cell_value = _get_cell_value
write_sheet = _write_sheet
save_excel = _save_excel
add_sheet = _add_sheet
