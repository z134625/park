import park
from parkPro.utils import base
from park import setting


park.go()


if __name__ == '__main__':
    env.load(show=False, path='./co.json')
    p = env['gpt_flask']
    p.main(['--start'], delay=0.2, epoch_show=False)
    # c = env['parkOrm']
    # cr = c.connect('sqlite3', path='./test.db').cr.cursor()
    # cr.execute('CREATE TABLE test (id int auto_increment, name varchar(20))')
