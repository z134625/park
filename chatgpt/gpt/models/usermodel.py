from parkPro.utils import api, base
from parkPro.expand.orm import ParkFields


class UserModel(base.ParkLY):
    _name = 'flask.user'
    _inherit = 'model'

    name = ParkFields.CharField(length=128, unique=True, null=False)
    display_name = ParkFields.CharField(length=128)
    age = ParkFields.IntegerField(default=0)
    password = ParkFields.CharField(length=128, null=False)

    def generator_msg(self, msg):
        return self.env['flask.user.info'].create({
            'user_id': self.id,
            'msg': msg
        })


class UseInfoModel(base.ParkLY):
    _name = 'flask.user.info'
    _inherit = 'model'

    user_id = ParkFields.ForeIgnFields(fk_model='flask.user')
    msg = ParkFields.CharField(length=256)


