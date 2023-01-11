import time
import httpx
import asyncio
import requests
from parkPro.tools import ParkLY, monitor, Paras, monitorV


def get_page_ajax_url(page):
    stamp = int(time.time() * 1000)
    url = "https://pagelet.mafengwo.cn/note/pagelet/recommendNoteApi?callback=" \
          "jQuery181015828549340406606_1669286769353" \
          "&params=%7B%22type%22%3A2%2C%22objid%22%3A10195%2C%22page%22%3A{page}%2C%22ajax" \
          "%22%3A1%2C%22retina%22%3A1%7D&_" \
          "={stamp}"
    return url.format(page=page, stamp=stamp)


def get_request_headers():
    headers = {
        'referer': 'https://www.mafengwo.cn/',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/107.0.0.0 Safari/537.36 Edg/107.0.1418.56',
    }
    return headers


class RequestParas(Paras):

    def init(self):
        return {
            'html': '',
            'url': '',
            'headers': {},
            'ips': [],
            'error_url': []
        }


class Request(ParkLY):
    _inherit = 'tools'

    def start(self):
        for i in range(1, 10):
            self.url = get_page_ajax_url(i)

    @monitorV('url', async_exec=True)
    async def request(self):
        async with httpx.AsyncClient() as client:
            response = await client.get(self.url, headers=self.headers)
            if response.status_code == 200:
                self.html = response.text
            else:
                self.error_url.append(self.url)

    @monitorV('html')
    def parsel_html(self):
        print(self.html)


if __name__ == '__main__':
    pass
