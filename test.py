
from parkPro.utils.api import monitor, monitorV
from parkPro.utils.base import ParkLY
from parkPro.utils.paras import Paras
from parkPro.utils.env import env
import re
import logging


# class TestParas(Paras):
#     @staticmethod
#     def init() -> dict:
#         _attrs = {
#             '_pos': 1
#         }
#         return locals()


class NewPark(ParkLY):
    _inherit = 'ParkLY'

    def __getitem__(self, item):
        if item.startswith('speed_info_'):
            func = re.match(r'^speed_info_([a-zA-Z_]\w+)', item)
            if func:
                if hasattr(self, func.group(1)):
                    eval('self.' + func.group(1) + '(park_time=True)')
            return super().__getattribute__('speed_info')
        else:
            return super().__getitem__(item)


class Test(ParkLY):
    _name = 'test'
    _inherit = 'monitor'
    root_func = ['tests']

    # paras = TestParas()

    def test(self):
        self.a = 100
        self.b = 1000
        self.c = None

    @monitorV('a')
    def tests(self):
        self.b = self.a * 10
        print(self._return)

    @monitor(['test', 'tests'])
    def _attrs(self):
        print(self._return)
        return 100


class P(ParkLY):
    _inherit = 'tools'

    def parse(self, response):
        print(response.text)
        return response

    # @monitor(['test', 'tests'])
    # def _attrs(self):
    #     print(1)


if __name__ == '__main__':
    env.load()
    p = env['setting']
    # p.update({'url': ['https://wwww.baidu.com', 'https://httpbin.org/get'], 'headers': {
    #     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'
    # }})
    # p.request(is_async=True)
    p.open(r'.\conf.py', park_time=True)
    print(p.speed_info)
    # p.number_dict.update({
    #     str(pow(10000, 4)): '兆'
    # })
    # print(p.number_to_chinese(1.78e+5, cash=True, park_test=True))
    # print(p.exists_rename('dasdas', park_time=True))
    # print(p.number_to_chinese_2(1.78e+5, park_test=True))
    # print(p.io['log'].getvalue())
    # p._attrs()
    # print(get_size(p))
    # test.test()
    # print(test.a)
    # print(test.b)
    # test.a = 1
    # print(test.b)
    # print(test._pos)