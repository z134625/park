import datetime
import os
import time
from multiprocessing import Process

import psutil

from .paras import RealTimeUpdateParas
from ...utils import api
from ...utils.api import MONITOR_FUNC
from ...utils.base import ParkLY


class RealTimeUpdate(ParkLY):
    _name = 'realtime'
    _inherit = ['monitor']
    paras = RealTimeUpdateParas()

    def start(self):
        return self._start()

    @api.monitor('_process', ty=MONITOR_FUNC)
    def add_process(self, func, args, kwargs):
        sub_p = Process(target=func, args=args, kwargs=kwargs)
        return {sub_p.pid: sub_p}

    def _start(self):
        self._start_parent()

    def _start_parent(self):
        path = os.getcwd()
        for sub in self._sub_process:
            sub.start()
        while True:
            if (self.context.start_time.second - datetime.datetime.now().second) % self.flush_time == 0:
                n = 0
                if os.stat(path).st_mtime > self.start_process and self._sub_process and n == 0:
                    for sub in self._sub_process:
                        sub.kill()
                    try:
                        psutil.Process(self._children_process_pid)
                    except psutil.NoSuchProcess:
                        print("loading....")
                        for sub in self._sub_process:
                            sub.start()
                            self.context.sub_pid = sub.pid
                        self.start_process = time.time()
                        n += 1

    def _process(self):
        sub = self._return
        if sub and isinstance(sub, dict):
            sub_pid = list(sub.keys())[0]
            self.context.sub_pid.append(sub_pid)
            self.context.sub_process.append(sub['sub_pid'])