from parkPro.utils import api, base


class Test(base.ParkLY):
    _name = 'gpt_flask'
    _inherit = 'flask'

    def flask_init(self):
        self.update({
            # 'css_paths': ['./css/index.css'],
            'css_paths': {'/': ['./css/index.css']},
            'setting_path': './conf.py',
        })

    @api.flask_route('/',
                     methods=['GET', 'POST']
                     )
    def main_web(self):
        if self.context.request.method == 'POST':
            openai = self.env['openai'].init_api(self.setting_path)
            msg = self.context.request.form["msg"]
            response = openai.test(msg)
            return self.render(result=response)
        return self.render('./template/index.html', result=None)