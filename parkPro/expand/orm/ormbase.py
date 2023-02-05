from ...utils import base, api
from .paras import ormParas


class IntellectBase(base.ParkLY):
    _name = 'parkOrm'
    paras = ormParas()

    def init(self,
             **kwargs
             ) -> None:
        super().init(**kwargs)
        self.register_fields(self.init_fields())

    def register_fields(self, fields: dict):
        register = """"""
        for key, value in fields.items():
            pass
        self.context.cr.execute(register)

    @staticmethod
    def init_fields() -> dict:
        pass

    def connect_sql(self,
                    host: str,
                    port: int,
                    user: str,
                    password: str,
                    dbname: str = None
                    ) -> None:
        pass