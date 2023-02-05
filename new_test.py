from chatgpt.gpt import Test
from parkPro.utils.env import env


if __name__ == '__main__':
    env.load(show=False)
    p = env['gpt_flask']
    print(p.__new_attrs__)
    # p.main(['--start'], delay=0.2, epoch_show=False)