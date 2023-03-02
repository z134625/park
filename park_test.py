from parkPro.utils.base import ParkLY
from parkPro.utils.env import env
from parkPro.utils import api
from parkPro.expand.orm import ParkFields, model_env
from parkPro import tools


class A(ParkLY):
    _name = 'A.park'
    _inherit = 'tools'

    @api.monitor(fields={api.MONITOR_ORDER_BEFORE: 'test2', api.MONITOR_ORDER_AFTER: 'test3'}, ty=api.MONITOR_FUNC)
    @api.monitor(fields={api.MONITOR_ORDER_BEFORE: 'a', api.MONITOR_ORDER_AFTER: 'b'}, ty=api.MONITOR_VAR)
    def test1(self):
        print(self.a)
        print(self.b)

    def test2(self):
        print(2)

    def test3(self):
        print(3)


class a(ParkLY):
    _name = 'test'
    _inherit = 'model'

    name = ParkFields.CharField(unique=True)
    age = ParkFields.IntegerField(length=12)
    balance = ParkFields.IntegerField(decimal=2, default=60)

    balance1 = ParkFields.FloatField(decimal=2, default=60)
    balance2 = ParkFields.FloatField(decimal=2, default=60)
    name1 = ParkFields.CharField(index=True)
    name2 = ParkFields.CharField(unique=True)


class b(ParkLY):
    _name = 'p.test'
    _inherit = 'model'

    head_id = ParkFields.ForeIgnFields(fk_model='test')
    name = ParkFields.CharField(length=16, index=True)
    sex = ParkFields.CharField(index=True, comment='性别')

    password = ParkFields.CharField(null=False, password=True)


if __name__ == '__main__':
    tools.v_project = [
        {'func': 'length', 'kwargs': {'min': 6, 'max': 12}},
        {'func': 'types', 'kwargs': {'a_z': True, 'A_Z': True, 'number': True, 'sign': True}},
    ]
    env.load(show=True, path='./co.json')
    k = env['p.test']
    # k.create({
    #     'name': 'cxk2',
    #     'sex': '男',
    #     'password': 'Qwe123!'
    # })
    print(k.read(['id', 'name', 'sex']))
    # # k.paras.update({'_error': False})
    # # k.test1(park_time=True)
    # # print(k.speed_info)
