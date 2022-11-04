from parkPro.tools import ParkLY, command, monitor


class Test(ParkLY):
    _name = 'test'
    _inherit = ['monitor', 'tools']

    def info(self):
        print(self._return)

    @monitor('info')
    @command(['-t', '--test'])
    def test(self):
        """
        这是测试
        """
        print('test -t, --test')
        return 'test'

    @monitor('info')
    @command(['--file', '-f'])
    def update(self, path):
        """
        这将打印路径
        """
        print(path)
        return 'update'


if __name__ == '__main__':
    t = Test(_warn=False)
    t.main()
    print(t.update('./'))
