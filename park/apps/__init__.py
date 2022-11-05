import pkgutil
import os.path
import os
import sys

from ..tools import Setting, _listPath, LISTALL
from typing import Iterator


class AppsSetting(Setting):
    _name = 'park.apps'

    def read(self) -> Iterator:
        apps = self.apps.split(',')
        for ap in apps:
            sys.path.append(ap)
            yield os.path.basename(ap)
            # for path in _listPath(ap, mode=LISTALL, list=True):
            #     if path.endswith('.py'):
            #         a = os.path.basename(path)
            #         yield a.split('.')[0]


app = AppsSetting(_error=False)

app.open(r'D:\Desktop\test\ParkTorch\conf.txt')

for i in app.read():
    exec(f'import {i}')
    # sys.modules.update({
    #     f'park.apps.{i}': __import__(i)
    # })
    __path__ += eval(f'{i}.__path__')

__path__ = [
    os.path.abspath(path)
    for path in pkgutil.extend_path(__path__, __name__)
]
print(__path__)