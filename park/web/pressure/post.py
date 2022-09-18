import abc
import httpx
import asyncio
import threading

from multiprocessing import Pool
from typing import Union, Iterable


class PostPressureTest(metaclass=abc.ABCMeta):
    def __init__(self, number: int = 100, concurrent: int = 10, pool: int = 4):
        self.number = number
        self.concurrent = concurrent
        self.url = self.get_url()
        self.async_loop = asyncio.get_event_loop()
        self.process_loop = Pool(pool)

    @abc.abstractmethod
    def get_url(self):
        url: Union[str, list, tuple] = ""
        return url

    def _async_test(self):
        async def request(url: str, sign: int) -> None:
            async with httpx.AsyncClient() as client:
                response = await client.post(url)
            status_code = response.status_code
            print(f'async_main: {threading.current_thread()}: {sign}:{status_code}')
        if isinstance(self.url, Iterable) and not isinstance(self.url, str):
            pass
        tasks = [request(url=self.url, sign=i) for i in range(self.number)]
        self.async_loop.run_until_complete(asyncio.wait(tasks))

    def _concurrent_test(self):
        self.process_loop.apply_async()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.async_loop.close()
        self.process_loop.close()
