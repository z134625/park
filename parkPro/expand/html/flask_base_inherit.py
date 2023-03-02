from parkPro.utils import base
from ... import setting


class ParkWeb(base.ParkLY):
    _inherit = 'flask'

    def init_setting(
            self,
            path: str
    ) -> None:
        res = super().init_setting(path)
        if res and self.setting_path:
            for key, value in self.SETTING.items():
                setting.var[key] = value
            self.env.load(show=False, path=self.setting_path, _type='orm')


