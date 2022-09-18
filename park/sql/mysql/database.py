
def create_database(db: str, character: str = None) -> str:
    """
    用于创建数据库，仅在不存在该数据库的情况下创建
    :param db: 创建数据库名
    :param character: 指定字符集
    :return: 一个sql语句
    """
    sql = 'CREATE DATABASE IF NOT EXISTS %s' % db
    if character:
        sql += ' CHARACTER SET %s' % character
    return sql + ';'


def show_databases(**kwargs) -> str:
    """
    用于列出所有数据库
    :param kwargs: 支持增加like 参数 用于模糊匹配包含该项的数据库
    :return: 一个sql语句
    """
    sql = 'SHOW DATABASES'
    like = kwargs.get('like', None)
    if like:
        # sql += f' LIKE \'%{like}%\''
        sql = f'SELECT schema_name FROM information_schema.schemata WHERE schema_name LIKE \'%{like}%\''
    return sql + ';'


def drop_database(db: str) -> str:
    """
    用于删除数据库
    :return: 一个sql语句
    """
    sql = 'DROP DATABASE IF EXISTS %s' % db
    return sql + ';'


def _test():
    """
    >>> create_database(database='park')
    'CREATE DATABASE IF NOT EXISTS park'
    >>> create_database(database='park', character='utf8')
    'CREATE DATABASE IF NOT EXISTS park CHARACTER SET utf8'
    >>> show_databases()
    'SHOW DATABASES'
    >>> show_databases(like='pa')
    "SELECT schema_name FROM information_schema.schemata WHERE schema_name LIKE '%pa%';"
    """
    # 本方法用于测试用例不返回任何内容


if __name__ == '__main__':
    import doctest

    doctest.testmod()
