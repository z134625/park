import datetime
import json
import re
from typing import Any, Union, List, Tuple

from parkPro.utils._type import JsonType
from parkPro import setting


class Fields:
    _type = 'int'
    unique = False
    null = True
    length = 32
    index = False
    default = None
    primary_key = False

    def __init__(self, **kwargs):
        self.unique = kwargs.get('unique', False)
        self.null = kwargs.get('null', True)
        self.primary_key = kwargs.get('primary_key', False)
        self.length = kwargs.get('length', 32)
        self.index = kwargs.get('index', False)
        self.default = kwargs.get('default', None)
        if getattr(setting, 'sql_type', 'sqlite') == 'mysql':
            self.comment = kwargs.get('comment', None)
        self._index = ['unique', 'index', 'primary_key']

    def __getattribute__(self, item):
        try:
            res = super().__getattribute__(item)
            return res
        except AttributeError:
            return False

    @classmethod
    def create_index(cls, fields, table, ty='create'):
        if ty == 'create':
            sql = ""
            for field in fields:
                if_e = ''
                if getattr(setting, 'sql_type', 'sqlite') == 'postgresql':
                    if_e = 'IF NOT EXISTS'
                sql += """
    CREATE INDEX {if_e} {field}_index ON {table}({field});
                """.format(field=field, table=table, if_e=if_e)
            return sql
        else:
            return [['ADD INDEX', field + '_index', 'ON', f'({field})'] for field in fields]

    def self(self, obj=None):
        ty = ''
        plug = []
        if self.unique:
            plug += ['UNIQUE']
        if not self.null:
            plug += ['NOT NULL']
        if self.null and getattr(setting, 'sql_type', 'sqlite') not in ['sqlite', 'postgresql']:
            plug += ['NULL']
        # if self.index:
        #     plug += ' INDEX '
        if self.default is not None:
            de = self.format(self.default)
            if de:
                plug += ['DEFAULT %s' % de]
        if self.comment and getattr(setting, 'sql_type', 'sqlite') == 'mysql':
            plug += ['COMMENT %s' % self.format(self.comment)]
        return ty, plug

    @classmethod
    def domain(cls, domain):
        do = []
        counter = 0
        if domain:
            for i, d in enumerate(domain):
                if d == '|':
                    counter += 2
                if len(d) == 3:
                    field = cls.format_fields(d[0])
                    sign = d[1]
                    result = cls.format(d[2])
                    if sign == 'like':
                        result = cls.format(f'%{d[2]}%')
                    d = [field, sign, result]
                    do.append(' '.join(d))
                    if i < len(domain) - 1:
                        if counter != 0:
                            counter -= 2
                            do.append('OR')
                        else:
                            do.append('AND')
        if not do:
            do.append('1 = 1')
        return ' '.join(do)

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
            sql = cls._create(ty='table', table=table, vals=vals, fk=kwargs.get('fk'))
        elif mode == 'update table':
            sql = cls._update(ty='table', table=table, vals=vals)
        elif mode == 'select':
            sql = cls._select(table=table, vals=vals, order=order, limit=limit)
        elif mode == 'select table':
            domain = cls.domain([('type', '=', 'table'), ('name', '=', 'test')])
            sql = cls._select(table='sqlite_master', vals=(['sql'], domain), order=order, limit=limit)
        elif mode == 'alter update':
            if getattr(setting, 'sql_type', 'sqlite') == 'sqlite':
                sql = ""
            elif getattr(setting, 'sql_type', 'sqlite') == 'mysql':
                sql = cls._alter(ty='MODIFY', table=table, vals=vals)
            elif getattr(setting, 'sql_type', 'sqlite') == 'postgresql':
                sql = cls._alter(ty='ALTER COLUMN', table=table, vals=vals)
        elif mode == 'alter add':
            if getattr(setting, 'sql_type', 'sqlite') == 'postgresql':
                sql = cls._alter(ty='ADD COLUMN', table=table, vals=vals)
            else:
                sql = cls._alter(ty='ADD', table=table, vals=vals)
        elif mode == 'alter del':
            if getattr(setting, 'sql_type', 'sqlite') == 'postgresql':
                sql = cls._alter(ty='DROP COLUMN', table=table, vals=vals)
            else:
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
            keys = map(lambda x: cls.format_fields(x), keys)
            sql = """
    INSERT INTO {table} ({ks}) VALUES ({vs});
            """.format(table=cls.format_table(table), ks=','.join(keys), vs=','.join(values))
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
        """.format(table=cls.format_table(table), vals=cls.format_fields(vals))
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
        elif callable(v):
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
        v = map(lambda x: cls.format_fields(x[0]) + ' ' + x[1][0] + ' ' + ' '.join(x[1][1]), vals.items())
        sql = """
CREATE TABLE IF NOT EXISTS {table} ({v}
        """.format(table=cls.format_table(table), v=','.join(v))
        if fk:
            sql += ","
            for kf, vf in fk.items():
                for fi in vf:
                    sql += """
CONSTRAINT {name}
FOREIGN KEY ({keys})
REFERENCES {model} (id)
                    """.format(model=kf.replace('.', '_'), keys=cls.format_fields(fi),
                               name=kf.replace('.', '_') + '_' + fi)
        sql += ");"
        return sql

    @classmethod
    def _update_table(cls, table, vals) -> Union[bool, str]:
        _vals = vals.items()
        if not _vals:
            return False
        ids, vs = list(_vals)[0]
        d = []
        for k, v in vs.items():
            d.append((k, '=', v))
        d = cls.domain(d)
        domain = cls.domain([('id', 'IN', ids)])
        sql = """
UPDATE 
    {table} 
SET 
    {v} 
WHERE 
    {domain}
        """.format(table=cls.format_table(table), v=d, domain=domain)
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
        keys = map(lambda x: cls.format_fields(x), keys)
        sql = """
SELECT 
    {vals}
FROM  {table}
WHERE 
    {where}
        """.format(table=cls.format_table(table), vals=','.join(keys), where=vals)
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
        """.format(table=cls.format_table(table), where=vals)
        return sql

    @classmethod
    def _alter(cls, ty, table, vals) -> str:
        sql = ""
        if 'ADD' in ty or 'DROP' in ty:
            if 'ADD' in ty:
                v = [str(k + ' ' + v[0] + ' '.join(v[1])) for k, v in vals.items()]
            else:
                v = [k + v for k, v in vals.items()]
            if v:
                sql = ""
                for kv in v:
                    sql += """
ALTER TABLE {table} {ty} {v};
                    """.format(table=cls.format_table(table), ty=ty, v=kv)
            return sql
        for k, v in vals.items():
            k = cls.format_fields(k)
            if getattr(setting, 'sql_type', 'sqlite') == 'mysql':
                if v.get('type'):
                    r = [v.get('type')] + v.get('attrs', [])
                    sql += """
ALTER TABLE {table} {ty} {k} {v};
                    """.format(table=table, ty=ty, k=k, v=' '.join(r))
            else:
                if v.get('type'):
                    if getattr(setting, 'sql_type', 'sqlite') == 'postgresql':
                        sql += """
ALTER TABLE {table} {ty} {k} TYPE {v};
                        """.format(table=table, ty=ty, k=k, v=v.get('type'))
                if v.get('attrs'):
                    for a_v in v.get('attrs'):
                        if getattr(setting, 'sql_type', 'sqlite') == 'postgresql':
                            sql += """
    ALTER TABLE {table} {ty} {k} SET {v};
                            """.format(table=table, ty=ty, k=k, v=a_v)
            if v.get('a_index'):
                for i in v.get('a_index'):
                    suffix = f'{table}_{k}_key'
                    if i == 'INDEX':
                        suffix = f'{table}_{k}_index'
                    if getattr(setting, 'sql_type', 'sqlite') == 'mysql':
                        sql += """
ALTER TABLE {table} ADD INDEX {name} ({k});
                        """.format(table=table, name=suffix, k=k)
                    elif getattr(setting, 'sql_type', 'sqlite') == 'postgresql':
                        index_type = ''
                        if i == 'UNIQUE':
                            index_type = 'UNIQUE'
                        sql += """
CREATE {index_type} INDEX IF NOT EXISTS {name} ON {table}({k});
                        """.format(index_type=index_type, table=table, name=suffix, k=k)
            if v.get('d_index'):
                for i in v.get('d_index'):
                    suffix = f'{table}_{k}_key'
                    if i == 'INDEX':
                        suffix = f'{table}_{k}_index'
                    if getattr(setting, 'sql_type', 'sqlite') == 'mysql':
                        sql += """
DROP INDEX {name} ON {table};
                        """.format(table=table, name=suffix)
                    elif getattr(setting, 'sql_type', 'sqlite') == 'postgresql':
                        sql += """
DROP INDEX IF EXISTS {name};
                        """.format(table=table, name=suffix)
        return sql

    def __get__(self, instance, owner):
        var = instance.fields.get(id(self))
        if var and instance.is_init:
            if var and len(instance) == 1:
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

    @staticmethod
    def format_fields(field):
        if getattr(setting, 'sql_type', 'sqlite') == 'postgresql':
            return f'"{field}"'
        return f'{field}'

    @classmethod
    def format_table(cls, table):
        if getattr(setting, 'sql_type', 'sqlite') == 'postgresql':
            return '"public"."%s"' % table
        return table


class IntegerField(Fields):
    _type = 'integer'

    def __init__(self, **kwargs):
        self.auto = kwargs.get('auto', False)
        super().__init__(**kwargs)

    def self(self, obj=None):
        if self.primary_key:
            self.null = False
        ty = 'INTEGER'
        _, plug = super(IntegerField, self).self(obj)
        if self.auto and getattr(setting, 'sql_type', 'sqlite') == 'postgresql':
            ty = 'SERIAL'
        if self.primary_key:
            plug += ['PRIMARY KEY']
        if self.auto:
            if getattr(setting, 'sql_type', 'sqlite') == 'mysql':
                plug += ['AUTO_INCREMENT']
            elif getattr(setting, 'sql_type', 'sqlite') == 'sqlite':
                plug += ['AUTOINCREMENT']
        return ty, plug


class CharField(Fields):
    _type = 'char'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.password = kwargs.get('password')

    def self(self, obj=None):
        ty = 'VARCHAR' + "(%d)" % int(self.length)
        _, plug = super(CharField, self).self(obj)
        return ty, plug


class FloatField(Fields):
    _type = 'float'

    decimal = 2

    def __init__(self, **kwargs):
        self.decimal = kwargs.get('decimal', 2)
        super().__init__(**kwargs)

    def self(self, obj=None):
        ty = 'NUMERIC' + "(%d, %d)" % (int(self.length), int(self.decimal))
        _, plug = super(FloatField, self).self(obj)
        return ty, plug


class DateField(Fields):
    _type = 'date'

    def self(self, obj=None):
        ty = 'DATE'
        _, plug = super(DateField, self).self(obj)
        return ty, plug

    @staticmethod
    def today():
        return datetime.date.today()


class DatetimeField(Fields):
    _type = 'datetime'

    def self(self, obj=None):
        ty = 'DATETIME'
        if getattr(setting, 'sql_type', 'sqlite') == 'postgresql':
            ty = 'TIMESTAMP'
        _, plug = super(DatetimeField, self).self(obj)
        return ty, plug

    @staticmethod
    def today():
        return datetime.datetime.today()


class JsonField(Fields):
    _type = 'json'

    def self(self, obj=None):
        ty = 'JSON'
        _, plug = super(JsonField, self).self(obj)
        return ty, plug

    @staticmethod
    def dumps(_Json: dict, **kwargs):
        return json.dumps(_Json, **kwargs)

    @staticmethod
    def loads(_Json: JsonType):
        return json.loads(_Json)

    def __get__(self, instance, owner):
        var = instance.fields.get(id(self))
        if var and instance.is_init:
            if var and len(instance) == 1:
                res = instance.read(var)[0][0]
                return res if isinstance(res, dict) else self.loads(res)
            return False
        else:
            return self


class ForeIgnFields(Fields):
    _type = 'foreign key'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.foreign_key = kwargs.get('fk_model')

    def self(self, obj=None):
        ty = 'INTEGER'
        _, plug = super(ForeIgnFields, self).self(obj)
        return ty, plug

    def __get__(self, instance, owner):
        var = instance.fields.get(id(self))
        if var and instance.is_init:
            if var and len(instance) == 1:
                return instance.env[self.foreign_key].browse(instance.read(var)[0][0])
            return False
        else:
            return self


class BoolFields(Fields):
    _type = 'bool'

    def self(self, obj=None):
        ty = 'CHAR'
        if getattr(setting, 'sql_type', 'sqlite') == 'postgresql':
            ty = 'BOOLEAN'
        _, plug = super(BoolFields, self).self(obj)
        return ty, plug

    def __get__(self, instance, owner):
        var = instance.fields.get(id(self))
        if var and instance.is_init:
            if var and len(instance) == 1:
                if getattr(setting, 'sql_type', 'sqlite') != 'postgresql':
                    return eval(instance.read(var)[0][0])
                return instance.read(var)[0][0]
            return False
        else:
            return self
