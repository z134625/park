import sqlite3
from typing import Any, Union, List, Tuple

import pymysql
import psycopg2

from ...utils import base
from .paras import ormParas
from ...utils._type import _ParkLY


class ConnectBase(base.ParkLY):
    _name = 'parkOrm'
    paras = ormParas()

    def connect(
            self,
            sql: str = None,
            **kwargs
    ) -> Union[_ParkLY, None]:
        if not kwargs:
            if not hasattr(self, 'SQL_TYPE'):
                return
            if self.SQL_TYPE == 'sqlite3':
                sql = 'sqlite3'
                kwargs = {
                    'path': self.SQL_PATH
                }
            else:
                sql = 'mysql'
                kwargs = {
                    'host': self.SQL_HOST,
                    'port': self.SQL_PORT,
                    'user': self.SQL_USER,
                    'password': self.SQL_PASSWORD,
                    'dbname': self.SQL_DBNAME,
                }
        return self._get_type_func(ty='connect_sql', key=sql, args=kwargs)

    def _connect_sql_sqlite3(
            self,
            path: str,
    ) -> _ParkLY:
        cr = sqlite3.connect(path, check_same_thread=False)
        self.update({
            'cr': cr.cursor(),
            'connection': cr,
        })
        return self

    def _connect_sql_mysql(
            self,
            user: str,
            password: str,
            database: str,
            host: str,
            port: int,
    ) -> _ParkLY:
        cr = pymysql.Connection(user=user,
                                password=password,
                                database=database,
                                host=host,
                                port=port)
        self.update({
            'cr': cr.cursor(),
            'connection': cr,
        })
        return self

    @property
    def cr(
            self
    ) -> sqlite3.Cursor:
        return self.cr

    @property
    def connection(
            self
    ) -> sqlite3.Connection:
        return self.connection

    def execute(
            self,
            s: str,
            **kwargs
    ) -> Union[bool, List[Union[Tuple]]]:
        method = 'fetchall'
        if kwargs.get('one'):
            method = 'fetchone'
        try:
            self.cr.execute(s)
            res = eval(f'self.cr.{method}()')
            self.connection.commit()
        except Exception as e:
            self.env.log.error(e)
            self.connection.rollback()
            return False
        return res
