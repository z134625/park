from ...utils.data import RequestInfo, RenderData
from ...conf.setting import Command
from . import server
from ...decorator import park


class ParkWeb:
    not_found = "404 ERROR"

    def __init__(self):
        self.request = None
        self.routes = {}

    def route(self, route, method: set = None):
        if method is None:
            method = {"GET"}
        self.routes[route] = None

        def wrapper(func, *args, **kwargs):
            self.routes[route] = {
                "func": func(self.request, *args, **kwargs),
                "method": method
            }
        return wrapper

    def _application(self, environ, start_response):

        self.request = RequestInfo(environ)
        method = self.request['REQUEST_METHOD']
        route = environ['PATH_INFO']
        if route in self.routes:
            result = self.routes[route]
            if method in result["method"]:
                response = result["func"]
                if isinstance(response, str):
                    start_response('200 OK', [('Content-Type', 'text/html')])
                    return [response.encode('utf-8')]

                elif isinstance(response, RenderData):
                    start_response("%d ok" % response.status, [('Content-Type', 'text/html')])
                    return [response.html.encode('utf-8')]
                else:
                    start_response('200 OK', [('Content-Type', 'text/html')])
                    return [response.encode('utf-8')]
            else:
                return ["NOT ALLOW THIS METHOD!".encode('utf-8')]
        else:
            start_response('404 OK', [('Content-Type', 'text/html')])
            return [self.not_found.encode('utf-8')]

    def start(self, port: int = 8888):

        port = int(port)
        if '--port' in Command or '-p' in Command:
            port_index = Command.index("--port") if '--port' in Command else Command.index("-p")
            port = int(Command[port_index + 1])
        park['server.start'](self._application, port=port)
