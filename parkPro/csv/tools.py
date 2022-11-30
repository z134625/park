import csv
from ..tools import ParkLY, Paras, monitor


class ParkCR:

    def __init__(self, ty):
        self.type = ty


class CSVParas(Paras):
    @staticmethod
    def init() -> dict:
        _attrs = {
            '_cr': ParkCR,
            'type': 'csv',
            '_type': 'csv'
        }
        return locals()


class CSVTools(ParkLY):
    _name = 'csv'
    _inherit = 'monitor'
    paras = CSVParas()

    @monitor('type')
    def _update_type(self):
        self._type = self.type
        if self._type in self._cr:
            self.cr = self._cr = ParkCR(self._type)
        else:
            raise KeyError(f'没有该类型文件({self._type})的操作方式')


