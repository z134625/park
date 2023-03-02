import gpt
from parkPro.utils.env import env


env.load(show=False)


if __name__ == '__main__':
    app = env['gpt']
    app.main(['--start'], delay=0.2, epoch_show=False)
