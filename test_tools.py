from parkPro.tools import ParkLY, command, monitor, monitorV, Paras
import logging

class TestParas(Paras):

    @staticmethod
    def init() -> dict:
        _attrs = {'i': -1, 'a': 0}
        return locals()


class Test(ParkLY):
    _name = 'test'
    _inherit = ['monitor', 'command']
    root_func = ['main']
    paras = TestParas()

    def info(self):
        self.i += 1
        self.a += 1

        logging.info('info')

    @monitorV('i', a=1)
    @command(['-t', '--test'], unique=False)
    def test(self, a):
        """
        这是测试
        """
        return self.i

    @monitor('info')
    @command(['--file', '-f'], unique=False)
    def update(self, a):
        for _ in range(10000):
            self.i += 1
        return 'update'


if __name__ == '__main__':
    t = Test(_warn=False)

    t.main()