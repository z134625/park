from parkPro.tools import monitor, ParkLY, monitorV
import parkPro.image


class Test(ParkLY):
    _name = 'test'
    _inherit = 'monitor'
    root_func = ['tests']

    def test(self):
        self.a = 100
        self.b = 1000
        self.c = None

    @monitorV('a')
    def tests(self):
        self.b = self.a * 10

    @monitor(['tests', 'test'])
    def attrs(self):
        print(self._return)
        return 100


if __name__ == '__main__':
    test = Test()
    test.test()
    print(test.a)
    print(test.b)
    test.a = 1
    print(test.b)
