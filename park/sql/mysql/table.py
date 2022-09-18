import warnings
from enum import Enum
from typing import Iterable, Union

from .dict_generator import dict_sql, list_sql


def create_table(table: str, **kwargs) -> str:
    """
    创建一个数据表
    :param table:  创建表的名
    :param kwargs: 必须传入columns，为列的字典, 可选参数engine, primary_key
    :return: 一个sql 语句
    columns 字典形式写法
    {
        "id": int,
        "name": str,
        "sex": tuple,
    }
    支持增加参数例：
    {
        "id": {
            "val": 1,
            "null": False,
        },
    {
        "name": {
            "val": '255',
            "variable": True,
        },
        "age": 1,
    }

    CREATE TABLE user (name VARCHAR(255) NOT NULL, age INT NOT NULL, PRIMARY KEY (name))ENGINE Innodb;
    创建的列包含id: 整数形式， name 字符串形式， tuple 枚举类型
    """
    engine = kwargs.get('engine', 'Innodb')
    columns = kwargs.get('columns', None)
    temporary = kwargs.get("temporary", False)
    assert columns and isinstance(columns, dict), "创建用户表必须提供columns， 并以字典形式"
    primary_key = kwargs.get('primary_key', None)
    columns = dict_sql(columns, table=True, primary_key=primary_key)
    sql = 'CREATE TABLE IF NOT EXISTS %s' % table
    if temporary:
        sql = 'CREATE TEMPORARY TABLE IF NOT EXISTS %s' % table
    sql += ' (%s)ENGINE %s' % (columns, engine)
    return sql + ';'


def show_tables(**kwargs) -> str:
    """
    用于显示该数据库中表
    :param kwargs: 支持like参数， 用于模糊匹配， 支持from_属性，不提供则显示当前数据库，提供将显示提供的数据库中的表
    :return: 一个sql语句
    """
    like = kwargs.get('like', None)
    from_ = kwargs.get('from_', None)
    full = kwargs.get('full', False)
    sql = 'SHOW %s TABLES' % 'FULL' if full else ''
    if from_:
        sql += ' FROM %s' % from_
    if like:
        sql += f' LIKE \'%{like}%\''
    return sql + ';'


def desc_table(table: str, **kwargs) -> str:
    """
    用于展示表的结构
    :param table: 表名
    :param kwargs:
    :return: 一个sql 语句
    """
    db = kwargs.get('db', None)
    table = f'{db}.{table}' if db else table
    sql = 'DESCRIBE %s' % table
    return sql + ';'


def change_table(table: str, **kwargs) -> str:
    """
    用于修改表的信息
    :param table: 表名
    :param kwargs: 只能传入一个参数，多传入无效，
    以add_columns, change_column_name, change_column_type, drop_column,顺序
    :return:  一个sql 语句
    """
    db = kwargs.get('db', None)
    table = f'{db}.{table}' if db else table
    basics = 'ALTER TABLE %s' % table

    add_columns = kwargs.get("add_columns", None)
    if add_columns:
        assert isinstance(add_columns, dict), "不支持非字典形式添加列"
        for key in add_columns:
            basics += ' ADD COLUMN %s,' % dict_sql({key: add_columns[key]}, table=True)
        return basics[:-1] + ';'

    change_column_name = kwargs.get("change_column_name", None)
    if change_column_name:
        assert isinstance(change_column_name, tuple) and change_column_name.__len__() == 2, \
            "请传入正确的格式修改列名(old_name, new_name)"
        assert isinstance(change_column_name[0], str) and isinstance(change_column_name[1], dict), \
            "请传入正确列名, 与修改内容"
        basics += ' CHANGE COLUMN `{}` {}'.format(change_column_name[0], dict_sql(change_column_name[1], table=True))
        return basics + ';'

    change_column_type = kwargs.get("change_column_type", None)
    if change_column_type:
        assert isinstance(change_column_type, dict), "若改变列类型，需要传入字典形式"
        basics += ', '.join([' MODIFY %s' % dict_sql({key: change_column_type[key]},
                                                     table=True) for key in change_column_type])
        return basics + ';'

    drop_column = kwargs.get("drop_column", None)
    if drop_column:
        if isinstance(drop_column, Iterable) and not isinstance(drop_column, str):
            basics += ', '.join(' DROP `%s`' % column for column in drop_column)
        else:
            basics += ' DROP %s' % drop_column
        return basics + ';'


def rename_table(tables: Union[list, str], new_tables: Union[list, str], **kwargs) -> str:
    """
    用于修改表名
    :param tables: 老表名， 可字符串可列表
    :param new_tables:  新表名， 修改顺序必须与老表一致
    :param kwargs: 支持mode 参数 默认rename, alter， 两种不同的sql， 第二种只能修改一个表名
    :return: 一个sql 语句
    """
    mode = kwargs.get("mode", "rename").lower()
    db = kwargs.get('db', None)
    if mode == "rename":
        sql = 'RENAME TABLE '
    elif mode == 'alter':
        waring = __import__("warnings")
        waring.warn("该模式下，只能生成修改一个表的sql语句，若传入列表，默认选取第一个元素", RuntimeWarning, stacklevel=2)
        table = tables if isinstance(tables, str) else tables[0]
        new_table = new_tables if isinstance(new_tables, str) else new_tables[0]
        table = f'{db}.{table}' if db else table
        new_table = f'{db}.{new_table}' if db else new_table
        sql = 'ALTER TABLE `%s` RENAME TO `%s`' % (table,
                                                   new_table)
        return sql + ';'
    else:
        raise ValueError("没有该模式")
    if (isinstance(tables, Iterable) and isinstance(new_tables, Iterable)) and \
            not (isinstance(tables, str) and isinstance(new_tables, str)):
        to_name = ', '.join(['`%s` TO `%s`' %
                             (f'{db}.{old}' if db else old,
                              f'{db}.{new}' if db else new)
                             for old, new in zip(tables, new_tables)])
    else:
        table = f'{db}.{tables}' if db else tables
        new_table = f'{db}.{new_tables}' if db else new_tables
        to_name = '`%s` TO `%s`' % (table, new_table)
    return sql + to_name + ';'


def truncate_table(table: str, **kwargs) -> str:
    """
    用于清空表中的数据
    :param table: 清空表的表名
    :param kwargs: 支持db筛选数据库
    :return: 一个sql语句
    """
    db = kwargs.get('db', None)
    table = f'{db}.{table}' if db else table
    sql = 'TRUNCATE TABLE %s' % table
    return sql + ';'


def drop_table(table: str, **kwargs) -> str:
    """
    用于删除表
    :param table: 删除表名
    :param kwargs: 支持db选择数据库， temporary 选择是否是删除临时表， 默认为否
    :return: 一个sql语句
    """
    temporary = kwargs.get('temporary', False)
    db = kwargs.get('db', None)
    table = f'{db}.{table}' if db else table
    sql = 'DROP TABLE if EXISTS %s' % table
    if temporary:
        sql = 'DROP TEMPORARY TABLE if EXISTS %s' % table
    return sql + ';'


def copy_table(old_table: str, new_table: str, **kwargs) -> str:
    """
    用于复制克隆表
    :param old_table: 老表名
    :param new_table: 新表名， 即新创建的表
    :param kwargs: 支持db选择数据库， where筛选复制表中列的条件
    :return: 一个sql 语句
    """
    where = kwargs.get("where", None)
    db = kwargs.get('db', None)
    new_table = f'{db}.{new_table}' if db else new_table
    old_table = f'{db}.{old_table}' if db else old_table
    basics = 'CREATE TABLE IF NOT EXISTS %s SELECT * FROM %s' % (new_table, old_table)
    if where:
        assert isinstance(where, dict), "限制条件必须为字典格式"
        basics += ' WHERE %s ' % dict_sql(where)
    return basics + ';'


def repair_table(tables: Union[list, str], **kwargs) -> str:
    """
    用于修复表
    quick: 指快速修复，仅修复索引文件， 不允许修复数据文件
    extended： 一次创建一个索引并进行排序修复
    use_frm： 当 找不到> .MYI 索引文件,或者其头文件已损坏。
    USE-FRM选项通知MySQL不信任此文件头中存在的信息,并使用数据字典中提供的信息重新创建它， 无法与myisamchk 一起使用
    :param tables: 表名，可字符串可列表
    :param kwargs:  支持db选择数据库， quick， use_frm, extended
    :return: 一个sql 语句
    """
    db = kwargs.get('db', None)
    quick = kwargs.get('quick', False)
    use_frm = kwargs.get('use_frm', False)
    extended = kwargs.get('extended', False)
    sql = 'REPAIR TABLE %s' % (list_sql(tables, db=db, is_escape=False)
                               if isinstance(tables, list) else (f'{db}.{tables}' if db else tables))
    if quick:
        sql += ' QUICK'
    if use_frm:
        sql += ' USE_FRM'
    if extended:
        sql += ' EXTENDED'
    return sql + ';'


def show_columns(table: str, **kwargs) -> str:
    """
    用于显示表中的列
    :param table: 表名
    :param kwargs: 支持db选择数据库， 使用like模糊匹配，筛选显示的列， 支持full即显示详细信息
    :return:
    """
    like: str = kwargs.get('like', None)
    db: str = kwargs.get('db', None)
    full: bool = kwargs.get('full', False)
    basics: str = 'SHOW %s COLUMNS FROM %s' % ('FULL' if full else '', f'{db}.{table}' if db else table)
    if like:
        basics += ' LIKE \'%%s%ds\' ' % like
    return basics + ';'


def lock_or_unlock_table(table: Union[str, list], **kwargs) -> str:
    """
    用于锁表与解锁表
    :param table: 锁定表的名
    :param kwargs: 支持db选择数据库， mode，锁表模式， 默认为read 即锁表后只允许用户读取表 write 为只允许用户读取和写入表
    :return: 一个sql语句
    """
    db: str = kwargs.get('db', None)
    if isinstance(table, list):
        table: list = list(map(lambda x: f'{db}.{x}' if db else f'`{x}`', table))
    else:
        table: str = f'{db}.{table}' if db else f'`{table}`'
    lock: bool = kwargs.get('lock', True)
    mode: str = kwargs.get('mode', 'r')
    assert mode in ['r', 'w'], "锁表仅支持读锁，写锁"
    if mode == 'r':
        mode = ' READ'
    else:
        mode = ' WRITE'
    if lock:
        sql: str = 'LOCK TABLES %s' % (list_sql(table, add=mode, is_escape=False)
                                       if isinstance(table, list) else table + mode)
    else:
        sql: str = 'UNLOCK TABLES'
    return sql + ';'


def insert_rows(table: str, data: Union[dict, list], columns: list, **kwargs) -> str:
    """
    插入数据,若不确定插入数据的正确性，请打开ignore，这可忽视这些错误的数据，并不插入，
    :param table: 插入表的名
    :param data: 字典插入数据，key 为插入的列名， value 为插入的值
    :param columns: 指出插入数据的列名列表
    :param kwargs:支持db 选择数据库， many=True插入多组数据，data必须以列表，并且列表中为字典数据， ignore=True,可忽略插入的错误行
    :return: 一个sql语句
    """
    db: str = kwargs.get('db', None)
    many: bool = kwargs.get('many', False)
    ignore: bool = kwargs.get('ignore', False)
    duplicate_key: dict = kwargs.get('duplicate_key', None)
    table: str = f'{db}.{table}' if db else table
    ignore: str = ' IGNORE' if ignore else ""
    if isinstance(data, dict) and not many:
        sql: str = 'INSERT %s INTO %s(%s) VALUES (%s)' % \
                   (ignore, table, ', '.join(map(lambda x: f'`{x}`', columns)), dict_sql(data,
                                                                                         values=True,
                                                                                         columns=columns,
                                                                                         ))
    elif many and (isinstance(data, list) or isinstance(data, tuple)):
        sql: str = 'INSERT %s INTO %s(%s) VALUES %s' % (ignore, table, ', '.join(map(lambda x: f'`{x}`', columns)),
                                                        ', '.join(['(%s)' % (dict_sql(item,
                                                                                      values=True,
                                                                                      columns=columns
                                                                                      )) for item in data]))

    else:
        raise ValueError("many=True, data必须为列表形式，并且列表中储存字典数据")
    if duplicate_key:
        sql += ' ON DUPLICATE KET UPDATE %s' % dict_sql(duplicate_key)
    return sql + ';'


def select_rows(table: str, **kwargs) -> str:
    """
    用于查询操作
    :param table: 表名
    :param kwargs: 支持db查找数据库，选择显示的列， 是否进行去重操作， where 筛选条件， group分组操作
    :return:
    """
    db: str = kwargs.get('db', None)
    columns: list = kwargs.get('columns', None)
    distinct = kwargs.get('distinct', False)
    where: dict = kwargs.get('where', None)
    many: bool = kwargs.get('many', False)
    join = kwargs.get('join', False)
    union = kwargs.get('union', False)
    group: Union[str, list] = kwargs.get('group', None)
    having: dict = kwargs.get('having', None)
    order: Union[str, list] = kwargs.get('order', None)
    offset: Union[tuple, int] = kwargs.get('offset', None)
    limit: Union[tuple, int] = kwargs.get('limit', None)
    table = f'{db}.{table}' if db else '`%s`' % table
    if many:
        pass
    basics = 'SELECT %s %s FROM %s' % ('DISTINCT' if distinct else '', list_sql(columns) if columns else '*', table)
    if where:
        basics += ' WHERE %s' % dict_sql(where)
    if group:
        basics += ' GROUP BY %s' % (list_sql(group) if isinstance(group, list) or isinstance(group, tuple) else group)
    if having:
        basics += ' HAVING %s' % dict_sql(having)
    if order:
        basics += 'ORDER BY %s' % (('`%s`' % order) if isinstance(order, str) else list_sql(order))
    if isinstance(offset, list) or isinstance(offset, tuple) or \
            isinstance(limit, list) or isinstance(limit, tuple):
        tup = None
        if isinstance(offset, list) or isinstance(offset, tuple):
            tup = offset
        if isinstance(limit, list) or isinstance(limit, tuple):
            tup = limit
        basics += ' LIMIT %s OFFSET %s' % (tup[1], tup[0])
    elif limit and offset:
        basics += ' LIMIT %s OFFSET %s' % (limit, offset)
    elif limit and not offset:
        basics += ' LIMIT %d' % limit
    return basics + ';'


def change_rows(table: str, change_data: dict, **kwargs) -> str:
    """
    用于改变列，
    ！！！:注意若不提供where 该sql将改变整个表中所有内容
    请谨慎使用！
    :param table:  表名
    :param change_data: 改变的数据，为字典类型key 为改变的列名， value 为改变的值
    :param kwargs: 支持db即选择数据库， where 即 筛选条件 warning 默认开启，开启则会弹出警告
    :return:  一个sql语句
    """
    db: str = kwargs.get('db', None)
    where: dict = kwargs.get('where', None)
    table: str = f'{db}.{table}' if db else table
    sql: str = 'UPDATE %s SET %s' % (table, dict_sql(change_data))
    sql = sql.replace('and', ',')
    if where:
        sql += ' WHERE %s' % dict_sql(where)
    if 'WHERE' not in sql and kwargs.get('warning', True):
        warnings.warn('当前没有限制行，将全部修改，请谨慎操作', RuntimeWarning, stacklevel=2)
    return sql + ';'


def replace_rows(table: str, replace_data: dict, **kwargs) -> str:
    """
    用于替换数据， 与插入类似， 若替换数据中存在主键等唯一数据，若该数据已存在，则会更新该列， 否则即插入新的一列
    :param table:  表名
    :param replace_data: 替换数据，字典类型
    :param kwargs: 支持db选择数据库
    :return:  一个sql 语句
    """
    db = kwargs.get('db', None)
    columns = list(replace_data.keys())
    table = f'{db}.{table}' if db else table
    sql = 'REPLACE INTO %s (%s) VALUES (%s)' % (table, list_sql(columns),
                                                dict_sql(replace_data, values=True, columns=columns))
    return sql + ';'


def drop_rows(table: str, **kwargs) -> str:
    """
    用于删除行
    ！！！:若不提供where，将删除所有行，与truncate_table方法效果一致，即
    DROP FROM table_name; == TRUNCATE TABLE table_name;执行效果一致
    请谨慎使用！
    :param table:  表名
    :param kwargs:  支持db 选择数据库， where筛选条件  warning 是否开启警告， 默认开启
    :return: 一个sql语句
    """
    db = kwargs.get('db', None)
    where = kwargs.get('where', None)
    table = f'{db}.{table}' if db else table
    sql = 'DELETE FROM %s ' % table
    if where:
        sql += ' WHERE %s' % dict_sql(where)
    if 'WHERE' not in sql and kwargs.get('warning', True):
        warnings.warn('当前没有限制行，将全部删除，请谨慎操作', RuntimeWarning, stacklevel=2)
    return sql + ';'


def _test():
    """
    """


if __name__ == '__main__':
    d = {
        # "name": {
        #     "val": '255',
        #     "variable": True,
        # },
        "age": {
            'val': 1,
            'default': 0,
            'comment': "年龄"
        },
        "sex": {
            'val': Enum("sex", ("男", "女")),
            'default': '男'
        },
        "info": {
            "val": "128",
            "text": True,
            'null': True,
        }
    }
    print(create_table(table="info", columns={
        "id": {
            "val": 1,
            "auto": True,
            "comment": "自增id"
        },
        "name": {
            "val": "128",
            "null": False,
            "comment": "姓名"
        },
    }, primary_key="id"))
    print(drop_table("park", temporary=True))
    print(change_table("info", add_columns=d))
    print(change_table("info", change_column_name=("info", {"comment": {"val": "255", "text": True, "null": True}})))
    print(change_table("info", change_column_type=d))
    print(rename_table(tables=["info", "park"], new_tables=["park", "psd"]))
    print(drop_table("info"))
    print(lock_or_unlock_table(table=["info"], db='test', lock=False, mode='r'))
    print(insert_rows(table="info", columns=["name", "age"], many=True, db='test', data=[{
        "name": "park",
        "age": 1,
    }, {
        "name": "p1",
        "age": 31,
    }, {
        "name": "p2",
        "age": 22,
    }, {
        "name": "p3",
        "age": 18,
    }, {
        "name": "p4",
        "age": 17,
    }, {
        "name": "p5",
        "age": 45,
    }]))
    print(change_rows(table="info", db='test', change_data={
        "name": "park",
        "ages": 3,
        "info": "padsal",
    }, where={"ages": 1}))
    print(drop_rows('info', db='test', where={
        "ages": 10
    }))

    print(repair_table(tables=['info', 'park'], db='test'))
    print(replace_rows(table='info', replace_data={
        "name": 'park',
        "ages": 10,
    }))
    print(change_rows(table='info', change_data={
        "age": 17
    }, where={"name": "p5"}))
    print(select_rows(table="info", db="test", columns=('age', ), distinct=True))
