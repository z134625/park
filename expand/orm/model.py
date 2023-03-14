import copy
from typing import Tuple, Union, List, Any

from ...tools import get_password
from ...utils import base, api, env

from .ParkFields import (
    Fields,
    IntegerField,
    CharField,
    JsonField,
    DatetimeField,
    ForeIgnFields,
    BoolFields
)

from ...utils._type import _ParkLY
from .paras import modelParas
from .model_env import model_env
from .. import setting


class Model(base.ParkLY):
    _name = 'model'
    _inherit = 'monitor'
    paras = modelParas()
    _type = 'orm'
    _table = None

    id = IntegerField(auto=True, primary_key=True)
    create_date = DatetimeField(null=False, default=lambda x: x.create_date.today(), comment='数据插入时间')

    def __init__(self, **kwargs):
        self.fields = {}
        self._fields = {}
        self.ids = []
        self._id = 0
        self.is_init = False
        super().__init__(**kwargs)
        self._table = self._name.replace('.', '_')

    def init(
            self,
            **kwargs
    ) -> None:
        super(Model, self).init(**kwargs)
        try:
            if not model_env.cr:
                info = {
                    'host': setting.host,
                    'port': setting.port,
                    'user': setting.user,
                    'password': setting.password,
                    'database': setting.database,
                }
                cr = self.env['parkOrm'].connect(sql_type=setting.sql_type, **info)
                model_env(cr=cr, E=self.env)
        except AttributeError:
            pass
        setattr(self, 'env', model_env)
        self.env._mapping.update({
            self._name: self
        })
        self.get_fields()

    def init_model(self):
        if self.env.cr:
            if self._name == 'model':
                self._delete_table()
            self._rename_table()
            self.is_init = True

    def _delete_table(self):
        pass

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
        self.is_init = False
        for f in self.fields.values():
            field = eval(f'self.{f}')
            if field and field.default and callable(field.default):
                vals.update({
                    f: field.default(self)
                })
            if field and field.password and f in vals:
                vals.update({f: get_password(vals[f])})

        self.is_init = True
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
        self.is_init = False
        for f in self.fields.values():
            field = eval(f'self.{f}')
            if field and field.password and f in vals:
                vals.update({f: get_password(vals[f])})
            if isinstance(field, BoolFields) \
                    and getattr(setting, 'sql_type', 'sqlite') != 'postgresql' and f in vals:
                vals.update({f: 'True' if vals[f] else 'False'})
        self.is_init = True
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
        obj.is_init = True
        obj.update({'is_init': True})
        obj.ids = []
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
        res = self.dict_read(fields='id', domain=domain, order=order, limit=limit)
        ids = [r['id'] for r in res]
        return ids

    def read(
            self,
            fields: Union[str, List[str], Tuple[str]] = None,
            domain: List[Tuple[str, str, str]] = None,
            order: str = None,
            limit: int = None,
    ) -> List[List[Union[bool, Any]]]:
        _fields = tuple(self.fields.values())
        if isinstance(fields, str):
            fields = [fields]
        elif fields is None:
            fields = _fields
        result = self.dict_read(fields=fields, domain=domain, order=order, limit=limit)
        if result:
            return [[res[key] for key in fields] for res in result]
        return [[False for _ in fields]]

    def dict_read(
            self,
            fields: Union[str, List[str], Tuple[str]] = None,
            domain: List[Tuple[str, str, str]] = None,
            order: str = None,
            limit: int = None,
    ):
        result = self._read(domain=domain, order=order, limit=limit)
        _fields = tuple(self.fields.values())
        if isinstance(fields, str):
            fields = [fields]
        elif fields is None:
            fields = _fields
        if result:
            result = [dict(zip(_fields, res)) for res in result]
            return [{d: res[d] for d in res if d in fields} for res in result]
        return []

    def _read(
            self,
            domain: List[Tuple[str, str, str]] = None,
            order: str = None,
            limit: int = None,
    ):
        if domain is None:
            domain = []
        _fields = tuple(self.fields.values())

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
        return result

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
                    f: (ty, plug)
                })


class ParkModel(base.ParkLY):
    _name = 'park.model'
    _inherit = 'model'

    model = CharField(unique=True, null=False, comment='表名')
    code = JsonField(comment='创建表Json文件')
    model_index = JsonField(comment='创建的索引字段')


class ExpendModel(base.ParkLY):
    _inherit = 'model'

    def _rename_table(
            self
    ) -> Union[bool, None, List[Union[Tuple]]]:
        if self._fields:
            models = {}
            self.is_init = False
            _index = []
            for f in self.fields.values():
                field = eval(f'self.{f}')
                if field and isinstance(field, ForeIgnFields):
                    if field.foreign_key in models:
                        models[field.foreign_key].append(f)
                    else:
                        models[field.foreign_key] = [f]
                if field and field.index:
                    _index.append(f)
            self.is_init = True
            create_sql = Fields.get(mode='create table',
                                    table=self._table,
                                    vals=self._fields,
                                    fk=models,
                                    ).strip()
            index_sql = Fields.create_index(fields=_index, table=self._table)
            flags = True
            if self._table != 'park_model' and self._table != 'model':
                code = JsonField.dumps(self._fields, ensure_ascii=False)
                _index = JsonField.dumps({i: '1' for i in _index}, ensure_ascii=False)
                obj = self.env['park.model'].search([('model', '=', self._table)])
                if obj:
                    code = obj.code
                    index = obj.model_index
                    if isinstance(index, dict):
                        index = JsonField.dumps(index, ensure_ascii=False)
                    if isinstance(code, dict):
                        code = JsonField.dumps(code, ensure_ascii=False)
                    code = JsonField.loads(code.replace('%park%', '\''))
                    index = JsonField.loads(index.replace('%park%', '\''))

                    code, _index, create_sql = self.change_table(code, self._fields, index, JsonField.loads(_index))
                    if code:
                        code = JsonField.dumps(code, ensure_ascii=False)
                        if self.env.cr.execute(create_sql) is not None:
                            val = {'code': str(code).replace('\'', '%park%'),
                                   'model_index': str(JsonField.dumps(_index,
                                                                      ensure_ascii=False)).replace('\'', '%park%')}
                            return obj.write(val)
                    flags = False
                else:
                    flags = False
                    if self.env.cr.execute(create_sql) is not None:
                        self.env.cr.execute(index_sql)
                        return obj.create({'code': str(code).replace('\'', '%park%'), 'model': self._table,
                                           'model_index': str(_index).replace('\'', '%park%')})
            if create_sql and flags and self.is_init and self._table != 'model':
                self.env.cr.execute(create_sql)
                self.env.cr.execute(index_sql)
                return

    def change_table(
            self,
            old: dict,
            new: dict,
            o_index: dict,
            n_index: dict
    ) -> Tuple[Union[dict, bool], dict, bool]:
        code = False
        create_sql = False
        r = {}
        a = {}
        d = {}
        keys = set(new.keys()).union(set(old.keys()))
        add_index = set(n_index.keys()).difference(o_index.keys())
        del_index = set(o_index.keys()).difference(n_index.keys())
        for key in keys:
            o = old.get(key)
            n = new.get(key)
            d_index = []
            a_index = []
            attrs = []
            if o and n and o[0] == n[0] and o[1] == n[1] and not add_index and not del_index:
                continue
            elif o and n and (o[0] != n[0] or o[1] != n[1]):
                r.update({key: {}})
                if o[0] != n[0]:
                    r[key]['type'] = n[0]
                if 'type' in r[key] and getattr(setting, 'sql_type', 'sqlite') == 'mysql':
                    attrs = n[1]
                elif o[1] != n[1]:
                    d_attr = set(o[1]).difference(set(n[1]))
                    a_attr = set(n[1]).difference(set(o[1]))
                    attrs = []
                    for d_a in d_attr:
                        if d_a in ['UNIQUE', 'PRIMARY KEY']:
                            d_index.append(d_a)
                    for a_a in a_attr:
                        if a_a in ['UNIQUE', 'PRIMARY KEY']:
                            a_index.append(a_a)
                    for attr in n[1]:
                        if attr not in ['UNIQUE', 'PRIMARY KEY']:
                            if getattr(setting, 'sql_type', 'sqlite') == 'mysql':
                                r[key]['type'] = n[0]
                            attrs.append(attr)

            elif not o and n:
                a.update({key: new.get(key)})
            elif o and not n:
                d.update({key: ''})
            elif not o and not n:
                d.update({key: ''})
            if key in add_index and key not in d:
                a_index.append('INDEX')
            elif key in del_index and key not in d:
                d_index.append('INDEX')
            if attrs or d_index or a_index:
                if key not in r:
                    r.update({key: {}})
                r[key].update({
                    'd_index': d_index,
                    'a_index': a_index,
                    'attrs': attrs,
                })
        if r or a or d:
            code = new
            create_sql = ''
            create_sql += self._alter('add', a)
            create_sql += self._alter('del', d)
            create_sql += self._alter('update', r)

        if r and getattr(setting, 'sql_type', 'sqlite') == 'sqlite':
            for i in r.keys():
                code.update({
                    i: old.get(i)
                })
        return code, n_index, create_sql

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
        return sql or ''


class ExpendFlask(base.ParkLY):
    _inherit = 'flask'

    @api.command(
        keyword=['-c', '--config'],
        name='path',
        unique=True,
        priority=0,
    )
    def path(self,
             path: str
             ) -> None:
        super().path(path)
        info = {
            'host': setting.host,
            'port': setting.port,
            'user': setting.user,
            'password': setting.password,
            'database': setting.database,
        }
        cr = self.env['parkOrm'].connect(sql_type=setting.sql_type, **info)
        self.env.load(_type='orm', show=False)
        model_env(cr=cr, E=self.env)
        model_env.load()