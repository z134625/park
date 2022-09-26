
from wsgiref.simple_server import make_server
from ...conf.os import isExists
from ...utils.data import RenderData
from ...decorator import register


@register
def render(html: str = None, status: int = 200):
    if isExists(html):
        with open(html, 'r') as f:
            return RenderData(f.read(), status)
    else:
        raise FileNotFoundError("该文件(%s)不存在， File is not found" % html)


@register
def start(function, host: str = 'localhost', port: int = 8888):
    """
    :param function:
    :param host:
    :param port:
    :return:
    """
    httpd = make_server(host=host, port=port, app=function)
    print('Start HTTP on port %d' % port)
    try:
        print('click http://%s:%d' % (host, port))
        httpd.serve_forever()
        # webbrowser.open('http://localhost:8888/xyz?abc')
        # httpd.handle_request()
    except Exception as e:
        raise e
    finally:
        print("Server Closed")

