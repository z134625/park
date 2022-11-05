from typing import Optional, Awaitable

from tornado import ioloop, web, options
from tornado.options import define, options
import os


define("port", default=8888, help="run on the given port", type=int)


class Application(web.Application):
    def __init__(self):
        handlers = [
            (r'/', MainHandler)
        ]
        settings = dict(
            cookie_sercet="YOU_CANT_GUESS_MY_SECRET",
            template_path=os.path.join(os.path.dirname(__file__), "template"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            xsrf_cookies=True,
        )
        super(Application, self).__init__(handlers, **settings)


class MainHandler(web.RequestHandler):
    def data_received(self, chunk: bytes) -> Optional[Awaitable[None]]:
        pass

    def get(self):
        self.render("index.html")


def main():
    options.parse_command_line()
    app = Application()
    app.listen(options.port)
    ioloop.IOLoop.current().start()


if __name__ == '__main__':
    main()