from parkPro.utils.base import ParkLY
from parkPro.utils.env import env
from parkPro.utils import api
from parkPro.expand.orm import ParkFields


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
    balance = ParkFields.FloatField(decimal=2, default=0.00)


class b(ParkLY):
    _name = 'p.test'
    _inherit = 'model'

    head_id = ParkFields.ForeIgnFields(fk_model='test')
    name = ParkFields.CharField(length=32)


if __name__ == '__main__':
    env.load(show=True)
    k = env['p.test']

    # # k.paras.update({'_error': False})
    # # k.test1(park_time=True)
    # # print(k.speed_info)
