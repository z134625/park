from typing import List
from .dict_generator import dict_sql, list_sql


def create_user(username: str,
                password: str,
                host: str = 'localhost'
                ) -> str:
    """
    创建mysql用户指令
    :param username: 创建用户名
    :param password: 用户密码
    :param host: 用户主机，默认为本地localhost
    :return: sql 语句
    """
    sql = "CREATE USER IF NOT EXISTS `%s`@`%s` IDENTIFIED BY '%s';" % (username, host, password)
    return sql


def drop_user(username: str, host: str = 'localhost') -> str:
    """
    用户删除用户
    :param username:  删除用户名
    :param host: 用户主机， 默认本地localhost
    :return: sql 语句
    """
    sql = "DROP USER IF EXISTS `%s`@`%s`" % (username, host)
    return sql + ';'


def list_users(columns: List[str] = None, **kwargs) -> str:
    """
    用于获取用户列表的sql
    :param columns: 查询用户的哪些信息默认用户名和主机，使用列表形式
    :param kwargs:  增加screen，表明查询的条件以字典的形式
    :return: sql 语句
    """
    if columns is None:
        columns = ['User', 'Host']
    sql = ("SELECT %s FROM mysql.user" % list_sql(columns))
    where = kwargs.get('where', None)
    if where is not None:
        if isinstance(where, dict):
            sql += " WHERE %s" % dict_sql(where)
    return sql + ';'


def change_user_password(new_password: str, username: str = None, host: str = 'localhost') -> str:
    """
    修改 密码
    这里有两种写法，适用于mysql8.0以上的版本
    :param new_password: 新密码字符串
    :param username:  修改密码的用户名
    :param host:  用户主机，默认本地localhost
    :return: sql语句
    """
    sql = "ALTER USER `%s`@`%s` IDENTIFIED BY '%s'" % (username, host, new_password)
    # sql = "SET PASSWORD FOR `%s`@`%s` = '%s'" % (username, new_password, host)
    return sql + ';'


def grant_user(username: str,
               power: list = None,
               host: str = 'localhost',
               db: str = '*',
               table: str = '*',
               column: str = None,
               **kwargs
               ) -> str:
    """
    用户授权
    on *.* 表示对全局有效， database.* 表示对该数据库有效
    database.table 表示对数据库中的table表有效

    :param power: 授权列表默认为select
    :param username: 授权用户名
    :param host:  用户主机，默认localhost
    :param db: 授权数据库，默认为* ，表示所有数据库
    :param table: 授权数据表， 默认为* ，表示所有数据库
    :param column: 授权表中的单个列
    :param kwargs: 增加stored， 即面向储存过程的授权(PROCEDURE), 以及proxy ,它使一个用户成为其他用户的代理。
    :return: sql 语句
    """
    if power is None:
        power = ['SELECT']
    stored = kwargs.get("stored", False)
    proxy = kwargs.get("proxy", False)
    sql = "GRANT %s ON %s %s.%s TO `%s`@`%s`;" % (list_sql(power, column=column, is_escape=False),
                                                  "PROCEDURE" if stored else "",
                                                  db, table,
                                                  username, host)
    if proxy:
        proxy_user = kwargs.get("proxy_user")
        sql = "GRANT PROXY ON `%s` FROM `%s`@`%s`" % (proxy_user, username, host)
    return sql + ';'


def revoke_user(username: str,
                power: list = None,
                host: str = 'localhost',
                db: str = '*',
                table: str = '*',
                column: str = None,
                **kwargs
                ) -> str:
    """
    用户撤销权力
    on *.* 表示对全局有效， database.* 表示对该数据库有效
    database.table 表示对数据库中的table表有效

    :param power: 撤销权力列表默认为select
    :param username: 撤销权力用户名
    :param host:  用户主机，默认localhost
    :param db: 撤销权力数据库，默认为* ，表示所有数据库
    :param table: 撤销权力数据表， 默认为* ，表示所有数据库
    :param column: 撤销权力表中的单个列
    :param kwargs: 增加stored， 即面向储存过程的撤销权力(PROCEDURE/FUNCTION), 以及proxy ,撤销它使一个用户成为其他用户的代理。
    :return: sql 语句
    """
    if power is None:
        power = ['SELECT']

    stored = kwargs.get("stored", False)
    proxy = kwargs.get("proxy", False)
    sql = "REVOKE %s ON %s %s.%s TO `%s`@`%s`;" % (list_sql(power, column=column),
                                                   "PROCEDURE" if stored else "", db, table,
                                                   username, host)
    if proxy:
        proxy_user = kwargs.get("proxy_user")
        sql = "REVOKE PROXY ON `%s` FROM `%s`@`%s`" % (proxy_user, username, host)
    return sql + ';'


def lock_or_unlock_user(username: str, host: str = 'localhost', **kwargs) -> str:
    """
    用于锁与解锁用户
    :param username:
    :param host:
    :param kwargs:
    :return:
    """
    lock = kwargs.get('lock', True)
    basics = 'ALTER USER `%s`@`%s`' % (username, host)
    if lock:
        basics += ' ACCOUNT LOCK'
    else:
        basics += ' ACCOUNT UNLOCK'
    return basics + ';'


def show_user_state(username: str, host: str = 'localhost') -> str:
    """
    用于显示用户状态是否被锁
    :param username:
    :param host:
    :return:
    """
    sql = 'SELECT `user`, `host`, `account_locked` FROM mysql.user WHERE `user` = \'%s\' AND `host` = \'%s\'' %\
          (username, host)
    return sql + ';'


def _test():
    """
    >>> create_user(username="park", password="123", host="localhost")
    "CREATE USER IF NOT EXISTS `park`@`localhost` IDENTIFIED BY '123';"
    >>> create_user(username='park', password='123', host='*')
    "CREATE USER `park`@`*` IDENTIFIED BY '123';"
    >>> list_users()
    'SELECT `User`, `Host` FROM mysql.user'
    >>> list_users(screen={"host": "localhost"})
    "SELECT `User`, `Host` FROM mysql.user WHERE `host` = 'localhost';"
    >>> drop_user(username="park", host="localhost")
    'DROP USER `park`@`localhost`;'
    >>> change_user_password(new_password="321", username="park", host="localhost")
    "ALTER USER `park`@`localhost` IDENTIFIED BY '321';"
    >>> grant_user(username='park', host='localhost')
    'GRANT SELECT ON  *.* TO `park`@`localhost`;'
    >>> grant_user(username='park', power=['SELECT', 'INSERT'], db='database')
    'GRANT SELECT, INSERT ON  database.* TO `park`@`localhost`;'
    >>> grant_user(username='park', column='col1')
    'GRANT SELECT(`col1`) ON  *.* TO `park`@`localhost`;'
    >>> grant_user(username='park', stored=True)
    'GRANT SELECT ON PROCEDURE *.* TO `park`@`localhost`;'
    >>> grant_user(username='park', proxy=True, proxy_user="root")
    'GRANT PROXY ON `root` FROM `park`@`localhost`;'
    """
    # 本方法用于测试用例不返回任何内容


if __name__ == '__main__':
    import doctest

    doctest.testmod()
