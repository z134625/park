import copy
import json
from typing import Tuple, Union, List, Any
from types import LambdaType

from ...utils import base, api, env
from .ormbase import ConnectBase
from .ParkFields import (
    Fields,
    IntegerField,
    CharField,
    JsonField,
    DatetimeField,
    ForeIgnFields
)
from . import ParkFields
from ...utils._type import _ParkLY
from .paras import modelParas


class Env(env.env.__class__):

    def __init__(
            self,
            cr: ConnectBase,
            E: env.env.__class__
    ):
        super().__init__()
        setattr(self, 'cr', cr)
        for app in E.apps:
            if hasattr(eval(f'E["{app}"]'), '_type') and eval(f'E["{app}"]._type') == 'orm':
                self._mapping.update({
                    app: E[app]
                })


class Model(base.ParkLY):
    _name = 'model'
    _inherit = 'monitor'
    paras = modelParas()
    _type = 'orm'

    id = IntegerField(auto=True, primary_key=True)
    create_date = DatetimeField(null=False, default=lambda x: x.create_date.today(), comment='数据插入时间')

    def __init__(self, **kwargs):
        self.fields = {}
        self._fields = {}
        self.ids = []
        self._id = 0
        self.is_init = False
        super().__init__(**kwargs)

    def init(
            self,
            **kwargs
    ) -> None:
        super(Model, self).init(**kwargs)
        setattr(self, 'env', Env(self.env['parkOrm'].connect('sqlite3', path='./test.db'), self.env))
        self.get_fields()
        self._rename_table()
        self.update({'is_init': True})

    def _rename_table(
            self
    ) -> Union[bool, List[Union[Tuple]]]:
        self._table = self._name.replace('.', '_')
        if self._fields:
            create_sql = Fields.get(mode='create table',
                                    table=self._table,
                                    vals=self._fields
                                    ).strip()
            flags = True
            if create_sql and flags and self.is_init and self._table != 'model':
                return self.env.cr.execute(create_sql)

    def change_table(
            self,
            old: dict,
            new: dict
    ) -> Tuple[Union[dict, bool], bool]:
        code = False
        create_sql = False
        r = {}
        a = {}
        d = {}
        keys = set(new.keys()).union(set(old.keys()))
        for key in keys:
            o = old.get(key)
            n = new.get(key)
            if o and n and ''.join(o.split(' ')) == ''.join(n.split(' ')):
                pass
            elif o and n and ''.join(o.split(' ')) != ''.join(n.split(' ')):
                r.update({key: new.get(key)})
            elif not o and n:
                a.update({key: new.get(key)})
            elif o and not n:
                d.update({key: ''})
            elif not o and not n:
                d.update({key: ''})
        if r or a or d:
            code = new
            create_sql = ''
            create_sql += self._alter('update', r)
            create_sql += self._alter('add', a)
            create_sql += self._alter('del', d)
        if r and ParkFields.sql_type == 'sqlite':
            for i in r.keys():
                code.update({
                    i: old.get(i)
                })
        return code, create_sql

    def _alter(
            self,
            ty: str,
            vals: Union[str, dict, tuple, list]
    ) -> str:
        sql = """"""
        if ty == 'update':
            sql = Fields.get(mode='alter update',
                             table=self._table,
                             vals=vals
                             )
        elif ty == 'add':
            sql = Fields.get(mode='alter add',
                             table=self._table,
                             vals=vals
                             )
        elif ty == 'del':
            sql = Fields.get(mode='alter del',
                             table=self._table,
                             vals=vals
                             )
        return sql + ';' if sql else ''

    def create(
            self,
            vals: dict
    ) -> _ParkLY:
        max_id = Fields.get(mode='max',
                            table=self._table,
                            vals='id'
                            )
        result = self.env.cr.execute(max_id, one=True)
        _id = 1
        if result and result[0]:
            _id = result[0] + 1
        for f in self.fields.values():
            self.update({'is_init': False})
            field = eval(f'self.{f}')
            if field and field.default and isinstance(field.default, LambdaType):
                vals.update({
                    f: field.default(self)
                })
        self.update({'is_init': True})
        sql = Fields.get(mode='insert',
                         table=self._table,
                         vals=vals
                         )
        self.env.cr.execute(sql)
        return self.browse(_id)

    def write(
            self,
            vals: dict
    ) -> bool:
        update_sql = Fields.get(mode='update table',
                                table=self._table,
                                vals={tuple(self.ids): vals}
                                )
        self.env.cr.execute(update_sql)
        return True

    def browse(
            self,
            _IDs: Union[int, list, tuple]
    ) -> _ParkLY:
        ids = []
        if isinstance(_IDs, int):
            _IDs = [_IDs]
        if self.ids:
            for i in _IDs:
                if i in self.ids:
                    ids.append(i)
        else:
            ids = _IDs
        obj = self.__class__()
        obj.ids = copy.deepcopy(ids)
        return obj

    def search(
            self,
            domain: List[Tuple[str, str, str]],
            order: str = None,
            limit: int = None,
    ) -> _ParkLY:
        ids = self._search(domain=domain, order=order, limit=limit)
        return self.browse(ids)

    def _search(
            self,
            domain: List[Tuple[str, str, str]],
            order: str = None,
            limit: int = None,
    ) -> List[int]:
        res = self.read(domain=domain, order=order, limit=limit)
        ids = []
        for r in res:
            if r[0]:
                ids.append(r[0])
        return ids

    def read(
            self,
            fields: Union[str, List[str], Tuple[str]] = None,
            domain: List[Tuple[str, str, str]] = None,
            order: str = None,
            limit: int = None,
    ) -> List[List[Union[bool, Any]]]:
        if domain is None:
            domain = []
        _fields = tuple(self.fields.values())
        if isinstance(fields, str):
            fields = [fields]
        elif fields is None:
            fields = _fields
        if self:
            domain += [('id', 'in', self.ids)]
        domain = Fields.domain(domain)
        sql = Fields.get(mode='select',
                         table=self._table,
                         vals=(_fields, domain),
                         order=order,
                         limit=limit,
                         )
        result = self.env.cr.execute(sql)
        if result:
            result = [dict(zip(_fields, res)) for res in result]
            self.ids = copy.deepcopy([r.get('id') for r in result])
            return [[res.get(key, False) for key in fields]for res in result]
        return [[False for _ in fields]]

    def unlink(self):
        domain = Fields.domain([('id', 'in', self.ids)])
        delete_sql = Fields.get(mode='delete table',
                                table=self._table,
                                vals=domain
                                )
        self.env.cr.execute(delete_sql)
        self.ids.clear()
        return self

    def __str__(
            self
    ) -> str:
        ids = map(lambda x: str(x), self.ids)
        return self._name + '(%s)' % (','.join(ids))

    def __bool__(
            self
    ) -> bool:
        return bool(self.ids)

    def __len__(
            self
    ) -> int:
        return len(self.ids)

    def __iter__(self):
        return self

    def __next__(self):
        self._id += 1
        if self._id > len(self.ids):
            self._id = 0
            raise StopIteration
        else:
            return self.__class__().browse(self.ids[self._id - 1])

    def get_fields(
            self
    ) -> None:
        for f in self.__new_attrs__:
            field = eval(f'self.{f}')
            if isinstance(field, Fields):
                self.fields.update({
                    id(field): f
                })
                ty, plug = field.self()
                self._fields.update({
                    f: ty + ' '.join(plug)
                })


class ParkModel(base.ParkLY):
    _name = 'park.model'
    _inherit = 'model'

    model = CharField(unique=True, null=False, comment='表名')
    code = JsonField(comment='创建表Json文件')


class ExpendModel(base.ParkLY):
    _inherit = 'model'

    def _rename_table(
            self
    ) -> Union[bool, List[Union[Tuple]]]:
        self._table = self._name.replace('.', '_')
        if self._fields:
            models = {}
            for f in self.fields.values():
                self.update({'is_init': False})
                field = eval(f'self.{f}')
                if field and isinstance(field, ForeIgnFields):
                    if field.foreign_key in models:
                        models[field.foreign_key].append(f)
                    else:
                        models[field.foreign_key] = [f]
            self.update({'is_init': True})
            create_sql = Fields.get(mode='create table',
                                    table=self._table,
                                    vals=self._fields,
                                    fk=models
                                    ).strip()
            flags = True
            if self._table != 'park_model' and self._table != 'model':
                code = json.dumps(self._fields)
                obj = self.env['park.model'].search([('model', '=', self._table)])
                if obj:
                    code = JsonField.loads(obj.code)
                    code, create_sql = self.change_table(code, self._fields)
                    if code:
                        code = JsonField.dumps(code)
                        obj.write({'code': str(code)})
                        if self.env.cr.execute(create_sql):
                            return obj.write({'code': str(code)})
                    flags = False
                else:
                    flags = False
                    if self.env.cr.execute(create_sql):
                        return obj.create({'code': str(code), 'model': self._table})
            if create_sql and flags and self.is_init and self._table != 'model':
                return self.env.cr.execute(create_sql)
