import requests
from typing import Union, Any


class ParkRequests(object):
    default_header = {
        "art": "pro",
        "park": "zly"
    }

    def __init__(self, url: str, method: str = "GET", data: Any = None, header: dict = None):
        self.url = url
        self.method = method.upper()
        self.data = data
        self.header = self.default_header
        if header:
            self.header = {**self.default_header, **header}

    def start(self):
        eval("self._%s()" % self.method)

    def _GET(self):
        print(f'requests.get(url="{self.url}", headers={self.header})')
        # return eval(f'requests.get(url="{self.url}", headers={self.header})')

    def _POST(self):
        print(f'requests.post(url="{self.url}", headers={self.header}, '
              f'{"data=%s" % self.data if isinstance(self.data, dict) else "json=%s" % self.data})')
        # return eval(f'requests.post(url="{self.url}", headers={self.header}, '
        #             f'{"data=%s" % self.data if isinstance(self.data, dict) else "json=%s" % self.data}')
