from typing import Union


def add_indexes(table: str, indexes: Union[list, tuple], **kwargs) -> str:
    """
    用于增加索引
    :param table: 表名
    :param indexes: 索引格式必须为元组形式 (添加索引的列名， 索引类型) 支持fulltext, unique, primary key, index, indexes
    :param kwargs: 支持db 选择数据库
    :return: 一个sql 语句
    """
    db = kwargs.get('db', None)
    table = f'{db}.{table}' if db else f'`{table}`'
    basics = 'ALTER TABLE %s' % table
    assert (isinstance(indexes, tuple) or isinstance(indexes, list)) and indexes.__len__() == 2, \
        "请传入正确的格式添加索引(index(可字符串，可列表), 索引类型)"
    columns = indexes[0]
    index_type = indexes[1]
    index_type_list = ['index', 'unique', 'fulltext', 'primary_key', 'indexes']
    assert index_type in index_type_list, "索引类型错误，不支持该索引(%s)" % index_type
    index_type = index_type.upper().replace('_', ' ')
    if index_type == 'INDEXES':
        assert isinstance(columns, list), "多列索引，必须传入列表的列名"
        basics += ' ADD INDEX (%s);' % (', '.join(['`%s`' % column for column in columns]))
        return basics
    if index_type == 'PRIMARY KEY':
        assert isinstance(columns, str) or columns.__len__() == 1, "主键索引，必须传入列名，不允许添加多个主键"
        if isinstance(columns, str):
            basics += ' ADD %s (`%s`)' % (index_type, columns)
        else:
            basics += ' ADD %s (`%s`)' % (index_type, columns[0])
        return basics
    if isinstance(columns, list):
        basics += ', '.join([' ADD %s (`%s`)' % (index_type, column) for column in columns])
    else:
        basics += ' ADD %s (`%s`)' % (index_type, columns)
    return basics + ';'


def drop_indexes(table: str, index: str, **kwargs) -> str:
    """
    用于删除索引， 仅支持一个一个删除
    :param table: 表名
    :param index: 删除的索引名
    :param kwargs: 支持db选择数据库
    :return:
    """
    db = kwargs.get('db', None)
    table = f'{db}.{table}' if db else f'`{table}`'
    sql = 'DROP INDEX `%s` FROM %s;' % (index, table)
    return sql


def show_indexes(table: str, **kwargs) -> str:
    """
    用于显示表中的索引
    :param table: 表名
    :param kwargs: 支持db选择数据库
    :return:
    """
    db = kwargs.get('db', None)
    sql = 'SHOW INDEXES IN `%s`' % table
    if db:
        sql += ' FROM `%s`' % db
    return sql


def create_index(table: str, index: str, column: str, **kwargs) -> str:
    """
    用于创建索引
    :param table: 表名
    :param index: 索引名
    :param column: 列名
    :param kwargs: 支持db选择数据库
    :return:
    """
    db = kwargs.get('db', None)
    table = f'{db}.{table}' if db else f'`{table}`'
    sql = 'CREATE INDEX `%s` ON %s(`%s`);' % (index, table, column)
    return sql


def _test() -> None:
    """

    """


if __name__ == '__main__':
    print(add_indexes(table='info', indexes=('name', 'unique')))