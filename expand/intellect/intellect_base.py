import functools
import time

from parkPro.utils import base, api
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

    def init(
            self,
            **kwargs
    ) -> None:
        super().init(**kwargs)
        self.init_base(self.init_setting())

    def check_init(
            self
    ) -> bool:
        return bool(self.context.is_init)

    def init_setting(
            self,
    ) -> None:
        ...

    def init_base(
            self,
            path: str = None
    ) -> None:
        if path is None:
            path = self.context.setting_path
        if not self.check_init():
            self.env['setting'].load('setting', args=(path,)).give(self)
            self.context.is_init = True

    # @api.monitor(fields='ab',
    #              args=lambda x: {'y': x.a, 'x': x.b},
    #              ty=api.MONITOR_FUNC
    #              )
    @functools.lru_cache()
    def ap(
            self
    ):
        self.a = 100
        self.b = 1000
        with self.progress(enum=False, epoch_show=True) as pg:
            for i in pg(range(2)):
                s = pg.epochs(func=m, bar=True)

    @api.monitor(fields='ap')
    @api.command(keyword=['--ap'], name='ab')
    # @api.reckon_by_time_run
    def ab(self):
        print(1)
