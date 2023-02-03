from parkPro.utils.base import ParkLY
from parkPro.utils.paras import Paras


class Inherit(ParkLY):
    _name = 'inherit'
    paras = Paras()
    root_func = ['park']

    def park(self):
        print(self._name)


# a = Inherit(_root=False)
# print(dir())