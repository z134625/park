import sqlite3
from sqlite3 import Connection

import pymysql

from ...utils import base, api
from .paras import ormParas


class IntellectBase(base.ParkLY):
    _name = 'parkOrm'
    paras = ormParas()

    def register_fields(self,
                        fields: dict
                        ):
        if '_table' not in fields or not fields['_table']:
            return
        _table = fields['_table']
        self.update({
            '_table': _table
        })
        register = f"""CREATE TABLE {_table}"""
        fields.pop('_table')
        for key, value in fields.items():
            pass
        self.context.cr.execute(register)

    @staticmethod
    def init_fields() -> dict:
        pass

    def connect(self, sql=None, **kwargs):
        if not kwargs:
            if hasattr(self, 'SQL_TYPE'):
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

    def _connect_sql_sqlite3(self,
                             path: str,
                             ):
        cr = sqlite3.connect(path, check_same_thread=False)
        self.update({
            'cr': cr
        })
        return self

    def _connect_sql_mysql(self,
                           user: str,
                           password: str,
                           database: str,
                           host: str,
                           port: int,
                           ) -> Connection:
        cr = pymysql.Connection(user=user,
                                password=password,
                                database=database,
                                host=host,
                                port=port)
        self.update({
            'cr': cr
        })
        return self
