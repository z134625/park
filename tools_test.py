from parkPro.tools import ParkLY, env


class Test(ParkLY):
    _inherit = 'tools'

    def urls(self):
        return ['https://www.baidu.com', 'https://321.com']

    def parse(self, response):
        # print(response.text)
        return response


if __name__ == '__main__':
    env.load()
    # print(env._mapping)
    t = env['tools']
    # print(t._method)
    import logging
    t.paras.update({
        '_attrs': {
            'headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
            },
        }
    })
    t.request(is_async=True)
    print(t._io['log'].getvalue())
    # print(t.error_url)