import functools
import time

from ...utils import base, api
from .paras import IntellectParas


def m(**kwargs):
    bar = kwargs.get('bar')
    def p(i):
        time.sleep(0.01)
    bar(p, [i for i in range(1200)])
    return 1


class IntellectBase(base.ParkLY):
    _name = 'intellect'
    _inherit = 'tools'
    paras = IntellectParas()

    def check_init(self) -> None:
        self.context.is_init = True

    @api.monitor(fields='ab',
                 args=lambda x: {'y': x.a, 'x': x.b},
                 ty=api.MONITOR_FUNC
                 )
    @functools.lru_cache()
    def ap(self):
        self.a = 100
        self.b = 1000
        # with self.progress(enum=False, epoch_show=True, log_file=None) as pg:
        #     for i in pg(range(1)):
        #         s = pg.epochs(func=m, bar=True)

    @functools.lru_cache()
    def ab(self, x, y):
       print(x - y)
