
from .ormbase import ConnectBase
from ...utils import env


class Env(env.env.__class__):

    def __init__(self):
        super().__init__()
        self.is_connect = False
        self.cr = False

    def __call__(
            self,
            cr: ConnectBase,
            E: env.env.__class__
    ):
        try:
            setattr(self, 'cr', cr)
            for app in E.apps:
                if hasattr(eval(f'E["{app}"]'), '_type') and eval(f'E["{app}"]._type') == 'orm':
                    self._mapping.update({
                        app: E[app]
                    })
            self.is_connect = True
        except Exception as e:
            self.log.error(e)
        return self

    def __getattribute__(self, item):
        res = super(Env, self).__getattribute__(item)
        if item == 'cr' and not self.is_connect:
            return False
        return res

    def __getitem__(self, item):
        res = super().__getitem__(item)
        res.ids.clear()
        return res

    def load_init(self):
        for key in self._mapping:
            self._mapping[key].init_model()


model_env = Env()