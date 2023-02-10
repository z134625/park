from chatgpt.gpt import Test
from parkPro.utils.env import env


if __name__ == '__main__':
    env.load(show=False)
    p = env['gpt_flask']
    p.main(['--start'], delay=0.2, epoch_show=False)
    # c = env['parkOrm']
    # cr = c.connect('sqlite3', path='./test.db').cr.cursor()
    # cr.execute('CREATE TABLE test (id int auto_increment, name varchar(20))')
