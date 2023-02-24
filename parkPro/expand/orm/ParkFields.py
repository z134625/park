import datetime
import json
import re
from typing import Any, Union, List, Tuple
from types import LambdaType

from parkPro.utils._type import JsonType

sql_type = 'sqlite'


class Fields:
    _type = 'int'
    unique = False
    null = True
    auto = False
    length = 32
    commit = ''
    index = False
    decimal = 2
    default = None
    primary_key = False

    def __init__(self, **kwargs):
        self.unique = kwargs.get('unique', False)
        self.null = kwargs.get('null', True)
        self.auto = kwargs.get('auto', False)
        self.primary_key = kwargs.get('primary_key', False)
        self.length = kwargs.get('length', 32)
        self.index = kwargs.get('index', False)
        self.decimal = kwargs.get('decimal', 2)
        self.default = kwargs.get('default', None)
        self.comment = kwargs.get('comment', None)

    def self(self, obj=None):
        ty = ''
        if self._type == 'integer':
            ty = 'INTEGER'
        elif self._type == 'float':
            ty = 'NUMERIC' + "(%d, %d)" % (int(self.length), int(self.decimal))
        elif self._type == 'char':
            ty = 'VARCHAR' + "(%d)" % int(self.length)
        elif self._type == 'date':
            ty = 'DATE'
        elif self._type == 'datetime':
            ty = 'DATETIME'
        elif self._type == 'json':
            ty = 'JSON'
        elif self._type == 'foreign key':
            ty = 'INTEGER'
        plug = []
        if self.unique:
            plug += ['UNIQUE']
        if not self.null:
            plug += ['NOT NULL']
        # if self.index:
        #     plug += ' INDEX '
        if self.default is not None:
            de = self.format(self.default)
            if de:
                plug += ['DEFAULT %s' % de]
        if self.comment and sql_type == 'mysql':
            plug += ['COMMENT %s' % self.format(self.comment)]
        return ty + ' ', plug

    @classmethod
    def domain(cls, domain, connect='AND', not_1=False):
        do = ['1 = 1']
        if not_1:
            do = []
        if domain:
            for d in domain:
                if len(d) == 3:
                    d = [d[0], d[1], cls.format(d[2])]
                    do.append(' '.join(d))
        connect = f' {connect} '
        return connect.join(do)

    @classmethod
    def get(
            cls,
            mode: str,
            table: str,
            vals: Any = None,
            order: str = None,
            limit: int = None,
            **kwargs,
    ) -> str:
        sql = ''
        if mode == 'insert':
            sql = cls._insert(table, vals)
        elif mode == 'max':
            sql = cls._max(table, vals)
        elif mode == 'create table':
            sql = cls._create(ty='table', table=table, vals=vals, fk=kwargs.get('fk', None))
        elif mode == 'update table':
            sql = cls._update(ty='table', table=table, vals=vals)
        elif mode == 'select':
            sql = cls._select(table=table, vals=vals, order=order, limit=limit)
        elif mode == 'select table':
            domain = cls.domain([('type', '=', 'table'), ('name', '=', 'test')])
            sql = cls._select(table='sqlite_master', vals=(['sql'], domain), order=order, limit=limit)
        elif mode == 'alter update':
            if sql_type == 'sqlite':
                sql = ""
            elif sql_type == 'mysql':
                sql = cls._alter(ty='MODIFY', table=table, vals=vals)
        elif mode == 'alter add':
            sql = cls._alter(ty='ADD', table=table, vals=vals)
        elif mode == 'alter del':
            sql = cls._alter(ty='DROP', table=table, vals=vals)
        elif mode == 'delete table':
            sql = cls._delete(table=table, vals=vals)
        return cls.format_sql(sql)

    @classmethod
    def _insert(
            cls,
            table: str,
            vals: Union[dict, List[dict], Tuple[dict]]
    ) -> str:
        if isinstance(vals, dict):
            vals = [vals]

        def _generate_insert_sql(_Vs):
            keys = []
            values = []
            for k, v in _Vs.items():
                keys.append(k)
                values.append(cls.format(v))
            sql = """
    INSERT INTO {table} ({ks}) VALUES ({vs});
            """.format(table=table, ks=','.join(keys), vs=','.join(values))
            return sql

        res = []
        for vs in vals:
            res.append(_generate_insert_sql(vs))
        return '\n'.join(res)

    @classmethod
    def _max(
            cls,
            table: str,
            vals: str
    ) -> str:
        sql = """
SELECT 
    MAX({vals})
FROM 
    {table}        
        """.format(table=table, vals=vals)
        return sql

    @staticmethod
    def format(
            v: Any,
    ) -> str:
        if isinstance(v, str):
            v = "'%s'" % v
        elif isinstance(v, (list, tuple)):
            v = list(v) + [-1, -1]
            v = "{v}".format(v=tuple(v))
        elif isinstance(v, (int, float)):
            v = f'{v}'
        elif isinstance(v, datetime.datetime):
            v = "'{datetime}'".format(datetime=v.strftime('%Y-%m-%d %H:%M:%S'))
        elif isinstance(v, datetime.date):
            v = "'{date}'".format(date=v.strftime('%Y-%m-%d'))
        elif isinstance(v, bool):
            v = "'t'" if v else "'f'"
        elif isinstance(v, bytes):
            v = "'{v}'".format(v=v)
        elif v is None:
            v = ''
        elif isinstance(v, LambdaType):
            v = ''
        return v

    @classmethod
    def _create(cls, ty, table, vals, fk=None) -> str:
        if ty == 'table':
            return cls._create_table(table, vals, fk)

    @classmethod
    def _update(cls, ty, table, vals) -> str:
        if ty == 'table':
            return cls._update_table(table, vals)

    @classmethod
    def _create_table(cls, table, vals, fk=None) -> str:
        v = map(lambda x: ' '.join(x), vals.items())
        sql = """
CREATE TABLE IF NOT EXISTS {table} ({v}
        """.format(table=table, v=','.join(v))
        if fk:
            sql += ","
            for kf, vf in fk.items():
                for fi in vf:
                    sql += """
CONSTRAINT {name}
FOREIGN KEY ({keys})
REFERENCES {model} (id)
                    """.format(model=kf.replace('.', '_'), keys=fi, name=kf.replace('.', '_') + '_' + fi)
        return sql + ")"

    @classmethod
    def _update_table(cls, table, vals) -> Union[bool, str]:
        _vals = vals.items()
        if not _vals:
            return False
        ids, vs = list(_vals)[0]
        d = []
        for k, v in vs.items():
            d.append((k, '=', v))
        d = cls.domain(d, connect=',', not_1=True)
        domain = cls.domain([('id', 'IN', ids)])
        sql = """
UPDATE 
    {table} 
SET 
    {v} 
WHERE 
    {domain}
        """.format(table=table, v=d, domain=domain)
        return sql

    @classmethod
    def _select(
            cls,
            table,
            vals,
            order,
            limit,
    ) -> str:
        keys, vals = vals
        sql = """
SELECT 
    {vals}
FROM  {table}
WHERE 
    {where}
        """.format(table=table, vals=','.join(keys), where=vals)
        if limit:
            sql += """
LIMIT {limit}
             """.format(limit=limit)
        if order:
            sql += """
ORDER BY {order}
            """.format(order=order)

        return sql

    @classmethod
    def _delete(cls, table, vals):
        sql = """
DELETE 
FROM  
    {table}
WHERE 
    {where}
        """.format(table=table, where=vals)
        return sql

    @classmethod
    def _alter(cls, ty, table, vals) -> str:
        v = [' '.join(vs) for vs in vals.items()]
        if v:
            sql = """
ALTER TABLE {table} {ty} {v}
            """.format(table=table, ty=ty, v=v[0])
        else:
            sql = ""
        return sql

    def __get__(self, instance, owner):
        var = instance.fields.get(id(self))
        if instance.is_init:
            if var and len(instance) == 1:
                if isinstance(self, ForeIgnFields):
                    return instance.env[self.foreign_key].browse(instance.read(var)[0][0])
                return instance.read(var)[0][0]
            return False
        else:
            return self

    def __set__(self, instance, values):
        var = instance.fields.get(id(self))
        if instance.is_init:
            if var:
                return instance.write({
                    var: values
                })
            return False
        else:
            return self

    @staticmethod
    def format_sql(sql):
        return re.sub(r'\s+', ' ', sql).strip()


class IntegerField(Fields):
    _type = 'integer'

    def self(self, obj=None):
        ty, plug = super(IntegerField, self).self(obj)
        if self.primary_key:
            plug += ['PRIMARY KEY']
        if self.auto:
            plug += ['AUTOINCREMENT']
        return ty, plug


class CharField(Fields):
    _type = 'char'


class FloatField(Fields):
    _type = 'float'


class DateField(Fields):
    _type = 'date'

    @staticmethod
    def today():
        return datetime.date.today()


class DatetimeField(Fields):
    _type = 'datetime'

    @staticmethod
    def today():
        return datetime.datetime.today()


class JsonField(Fields):
    _type = 'json'

    @staticmethod
    def dumps(_Json: dict):
        return json.dumps(_Json)

    @staticmethod
    def loads(_Json: JsonType):
        return json.loads(_Json)


class ForeIgnFields(Fields):
    _type = 'foreign key'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.foreign_key = kwargs.get('fk_model')
#
# FOREIGN KEY (department_id)
# REFERENCES departments(department_id)


