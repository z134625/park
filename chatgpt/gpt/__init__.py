import time
from flask import request, redirect, jsonify
from flask_socketio import SocketIO, emit
from parkPro.utils import api, base


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
        })
        self.context.update({
            'cr': self.env['parkOrm'].connect('sqlite3', path='./test.db').cr.cursor(),
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
            self.context.cr.execute("SELECT count(*) FROM test WHERE name = '%s'" % username)
            res = self.context.cr.fetchone()
            if res and res[0] != 0:
                return self.Response('./template/index.html',
                                     cookies={
                                         'username': username,
                                         'time': time.time(),
                                     },
                                     timeout=30,
                                     username=username,
                                     login_type=True
                                     )
            else:
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
            username = cookie.get('username')
            openai = self.env['openai'].get({'setting': self.setting}).init_api()
            msg = request.form["msg"]
            response = openai.test(msg)
            return jsonify({'msg': response})

