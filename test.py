from parkPro.tools import monitor, ParkLY
import parkPro.image
import sys




class Test(ParkLY):
    _inherit = 'monitor'
    root_func = ['tests']

    def test(self):
        self.env.load()
        obj = self.env['image']
        obj.compress_png(r'C:\Users\PC\Desktop')
        obj.compress_png(r'C:\Users\PC\Desktop')
        obj.compress_png(r'C:\Users\PC\Desktop')

    def tests(self):
        print(self._return)

    @monitor(['tests', 'test'])
    def attrs(self):
        print(self._return)
        return 100


if __name__ == '__main__':
    test = Test()
    test.attrs()
