import time
from flask import request, redirect, jsonify
from flask_socketio import SocketIO, emit
from parkPro.utils import api, base
from . import models


class Test(base.ParkLY):
    _name = 'gpt_flask'
    _inherit = 'flask'

    def flask_init(self):
        self.update({
            # 'css_paths': ['./css/index.css'],
            'css_paths_gl': ['./css/index.css', './css/room.css'],
            'js_paths_gl': ['./js/room.js'],
            # 'css_paths': {'/': ['./css/room.css']},
            'setting_path': './conf.py',
            'images_path': r'C:\Users\PC\Desktop'
        })
        self.context.update({
            'cr': self.env['parkOrm'].connect('sqlite3', path='./test.db').cr,
            'msg': {}
        })

    @api.flask_route('/',
                     methods=['GET']
                     )
    def main_web(self):
        cookie = request.cookies
        username = cookie.get('username')
        if not username:
            return redirect('/login')
        return self.render('./template/index.html', username=username, login_type=True)

    @api.flask_route('/login',
                     methods=['GET', 'POST']
                     )
    def login_web(self):
        if request.method == 'POST':
            username = request.form["username"]
            user = self.env['flask.user'].search([('name', '=', username)], limit=1)
            if user:
                return self.Response('./template/index.html',
                                     cookies={
                                         'username': username,
                                         'time': time.time(),
                                     },
                                     timeout=30,
                                     username=user.display_name,
                                     login_type=True
                                     )
            else:
                user.create({
                    'name': 'cxk',
                    'display_name': '蔡徐坤',
                    'age': 23,
                    'password': '1234'
                })
                return self.Response('./template/index.html',
                                     delete=True,
                                     cookies='all',
                                     login_type=False,
                                     login_error=True
                                     )
        cookie = request.cookies
        username = cookie.get('username')
        if not username:
            return self.Response('./template/index.html',
                                 delete=True,
                                 cookies='all',
                                 login_type=False
                                 )
        else:
            return redirect('/')

    @api.flask_route('/ws', methods=['POST'])
    def ws(self):
        if request.method == 'POST':
            cookie = request.cookies
            # username = cookie.get('username')
            user = self.env['flask.user'].search([('name', '=', 'cxk')], limit=1)
            # openai = self.env['openai'].get({'setting': self.setting}).init_api()
            msg = request.form["msg"]
            a = user.generator_msg(msg)
            # response = openai.test(msg)
            return jsonify({'msg': 123})

