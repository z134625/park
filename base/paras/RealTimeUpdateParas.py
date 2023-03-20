import datetime
from ...utils.paras import Paras
from ...tools import _Context


class RealTimeUpdateParas(Paras):
    @staticmethod
    def init() -> dict:
        context = _Context({
            'uid': None,
            'start_time': datetime.datetime.now,
            'parent_pid': None,
            'sub_pid': [],
            'sub_process': [],
        })
        return locals()