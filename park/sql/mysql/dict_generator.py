from enum import EnumMeta, Enum
from typing import Any


def dict_sql(dict_: dict, **kwargs) -> str:
    """
    用于字典生成sql格式语句
    开启table： 即生成 类似创建表设置列内容的方式
    开启values：必须传入columns列表， 用于插入数据生成 ('value2', 'value1') columns为(key2, key1)
    以上均不开启则得到， and 链接的内容， 用于条件语句`key` = 'value' and `key1` = 'value1'
    :param dict_:  字典数据
    :param kwargs: 支持table， values， columns， primary_key
    :return:
    """
    table = kwargs.get('table', False)
    values = kwargs.get('values', False)
    if table:
        primary_key = kwargs.get("primary_key", None)
        sql = ", ".join(["`%s` %s" % (key, _type(**dict_[key])
                                      if isinstance(dict_[key], dict) else _type(dict_[key])) for key in dict_])
        if primary_key:
            sql += ", PRIMARY KEY (`%s`)" % primary_key
        return sql
    if values:
        columns = kwargs.get('columns', None)
        assert columns, "必须指定插入顺序"
        sql = ', '.join(['%s' % (f'\'{dict_[key]}\'' if isinstance(dict_[key], str)
                                 else dict_[key]) for key in columns])
        return sql
    return ' and '.join(["`%s` = '%s'" % (key, dict_[key]) for key in dict_])


def list_sql(list_: list, **kwargs) -> str:
    """
    用于将列表生成 sql格式语句
    若column 为单个值则得到 value1(`column`), value2(`column`)
    若开启is_escape，默认开启 则得到 `value1`, `value2` 若存在add则 `value1` add , `value2` add 此项用于锁表add 为加如的锁类型
    若不开启则得到 value1， value2
    若存在db 则得到 db.value1, db.value2 ， 用于选择数据库中的表
    以上选项都不能重复，即开启一项则只能得到一个结果,若传入多个，则以column, db, is_escape的顺序
    :param list_: 需要转化的数据
    :param kwargs: 支持添加列column， 以及数据库db ， 或者自定义增加内容add
    :return:
    """
    columns = kwargs.get('column', None)
    add = kwargs.get('add', '')
    db = kwargs.get('db', None)
    if columns and isinstance(columns, str):
        return ", ".join(["%s(`%s`)" % (i, columns) for i in list_])
    if db:
        return ", ".join([f"%s.%s" % (db, key) for key in list_])
    if kwargs.get("is_escape", True):
        return ", ".join([f"`%s` {add}" % i for i in list_])
    else:
        return ", ".join([f"%s {add}" % key for key in list_])


def _type(val: Any, **kwargs) -> str:
    """
    根据传入数据的类型与值，生成匹配的sql 条件语句
    如果为需要整型的即传入任意整数即可，
    基础属性： null default comment
    :param val: 传入任意类型值，包括但不限于int， str， tuple， list等， 支持生成类型以实际情况为准，
     若没有该类型功能则统一生成字符串类型
    :param kwargs: 支持null, unique, auto,等参数, int 支持big, auto参数， str 支持variable， text, long
    :return: 返回根据该值得到的 类型
    """
    null = kwargs.get('null', False)
    default = kwargs.get('default', None)
    comment = kwargs.get('comment', None)
    datetime = __import__("datetime")

    def additional():
        add = ''
        if null:
            add += ' NULL'
        else:
            add += ' NOT NULL'
        if default:
            add += ' DEFAULT \'%s\'' % default
        if comment:
            add += ' COMMENT \'%s\'' % comment
        return add

    if isinstance(val, int):
        class_ = 'INT'
        if kwargs.get("big", False):
            class_ = 'BIGINT'
        if kwargs.get('auto', False):
            class_ += ' AUTO_INCREMENT'
        class_ += additional()
        return class_

    elif isinstance(val, str):
        class_ = 'VARCHAR(%s)' % val
        if not kwargs.get('variable', True):
            class_ = 'CHAR(%s)' % val
        if kwargs.get('text', False):
            class_ = 'TEXT(%s)' % val
        if kwargs.get('long', False):
            class_ = 'LONGTEXT(%s)' % val
        class_ += additional()
        return class_

    elif isinstance(val, EnumMeta):
        enums = sorted(val.__members__.items(), key=lambda x: x[1].value)
        items = ["'%s'" % i for i, v in enums]
        class_ = 'Enum(%s)' % (', '.join(items))
        class_ += additional()
        return class_

    elif isinstance(val, datetime.datetime):
        pass


if __name__ == '__main__':
    d = {
        "name": {
            "val": '255',
            "variable": True,
        },
        "age": 1,
        "sex": {
            'val': Enum("sex", ("男", "女")),
            'default': '男'
        },
        "info": {
            "val": "128",
            "text": True,
            "fulltext": "info",
        }
    }
    print(dict_sql(d, table=True))
