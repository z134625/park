from parkPro.tools import monitor, ParkLY, monitorV, Paras


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
    def attrs(self):
        print(self._return)
        return 100


if __name__ == '__main__':
    test = Test(_root=False)
    p = Paras()

    test.test()
    print(test.a)
    print(test.b)
    test.a = 1
    print(test.b)
    print(test._pos)
