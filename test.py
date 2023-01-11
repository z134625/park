from parkPro.tools import monitor, ParkLY, monitorV, Paras, env, get_size


# class TestParas(Paras):
#     @staticmethod
#     def init() -> dict:
#         _attrs = {
#             '_pos': 1
#         }
#         return locals()


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
    _inherit = 'test'

    @monitor(['test', 'tests'])
    def _attrs(self):
        print(1)



if __name__ == '__main__':
    env.load()
    p = env['tools']
    # p.number_dict.update({
    #     str(pow(10000, 5)): '兆'
    # })
    import time
    start_time = time.time()
    print(p.number_to_chinese('12340', cash=False, park_time=True))
    print(p.exists_rename('dasdas', park_time=True))
    end_time = time.time()
    print(end_time - start_time + 0.001 - 0.001)
    print(p.speed_info)
    # p._attrs()
    # print(get_size(p))0
    # test.test()
    # print(test.a)
    # print(test.b)
    # test.a = 1
    # print(test.b)
    # print(test._pos)