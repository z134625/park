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
            sql_type: str = None,
            **kwargs
    ) -> _ParkLY:
        try:
            self._get_type_func(ty='connect_sql', key=sql_type, args=kwargs)
        except Exception as e:
            self.env.log(e)
            self.update({
                'cr': None,
                'connection': None,
            })
        return self

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

    def _connect_sql_postgresql(
            self,
            user: str,
            password: str,
            database: str,
            host: str,
            port: int,
    ) -> _ParkLY:
        cr = psycopg2.connect(user=user,
                              password=password,
                              database=database,
                              host=host,
                              port=port)
        self.update({
            'cr': cr.cursor(),
            'connection': cr,
        })
        return self

    def execute(
            self,
            s: str,
            **kwargs
    ) -> Union[bool, None, List[Union[Tuple]]]:
        if not s:
            return True
        method = 'fetchall'
        if kwargs.get('one'):
            method = 'fetchone'
        try:
            for sql in s.split(';'):
                sql = sql.strip()
                if not sql:
                    continue
                self.cr.execute(sql)
                self.connection.commit()
            res = eval(f'self.cr.{method}()')
        except psycopg2.ProgrammingError as e:
            if 'no results to fetch' in str(e):
                self.connection.commit()
                return True
            self.env.log.error(e)
            self.connection.rollback()
            return None
        except Exception as e:
            self.env.log.error(e)
            self.connection.rollback()
            return None
        return res
