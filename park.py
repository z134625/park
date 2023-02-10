from parkPro.utils.base import ParkLY
from parkPro.utils.env import env


class Fields:

    def __init__(self, **kwargs):
        self.init(**kwargs)

    def init(self, **kwargs):
        pass

    def __get__(self, obj, cls=None):
        return self


class A(ParkLY):
    _name = 'A.park'
    c = Fields()

    def init(self, ** kwargs):
        super().init()
        __mapping__ = {}
        for k in self.__new_attrs__:
            if hasattr(self, k):
                v = eval(f'self.{k}')
                if isinstance(v, Fields):
                    __mapping__[k] = v
        setattr(self, '__mapping__', __mapping__)


if __name__ == '__main__':
    env.load()
    k = env['A.park']
    # k.init()
    print(k.__new_attrs__)
    print(k.__mapping__)
