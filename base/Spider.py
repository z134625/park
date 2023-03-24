import asyncio
import logging
import httpx
import requests

from io import BytesIO
from httpx import Response

from collections.abc import (
    Iterable,
)
from typing import (
    Union,
    Callable,
    Tuple,
    Any,
    Dict,
    Optional, List
)
from types import (
    MethodType,
    FunctionType
)

from .paras import SpiderParas
from ..utils import api
from ..utils.base import ParkLY
from ..utils.api import (
    MONITOR_FUNC,
    MONITOR_VAR
)


class Spider(ParkLY):
    _name = 'spider'
    _inherit = 'tools'
    paras = SpiderParas()

    def try_response(
            self,
            func: Union[MethodType, FunctionType]
    ) -> Callable[[Tuple[Any], Dict[str, Any]], Optional[Any]]:

        def warp(*args, **kwargs):
            method = self.context._method
            response = None
            _ = kwargs.get('_', 0)
            url = kwargs.get('url', None) or args[0]
            if '_' in kwargs:
                kwargs.pop('_')
            self.context._ = _ + 1
            error = False
            try:
                response = func(*args, **kwargs)
            except Exception as e:
                error = True
                logging.error(msg=f'{_ + 1} 次 ({method})请求失败 请求地址({url}) \n 原因：{e}')
            finally:
                if not error:
                    if response is None:
                        if error:
                            logging.debug(msg=f'{_ + 1} 次 ({method})未请求 请求地址({url})')
                    else:
                        if response.status_code == 200:
                            logging.debug(msg=f'{_ + 1} 次 ({method})请求成功 请求地址({url})')
                            return self._success_response(response)
                        else:
                            logging.debug(msg=f'{_ + 1} 次 ({method})请求失败({response.status_code}) 请求地址({url})')
                self.context.error_url.append(url)
                return response

        return warp

    def try_response_async(
            self,
            func: Any
    ) -> Callable[[Tuple[Any], Dict[str, Any]], Optional[Any]]:
        method = self.context._method

        async def warp(*args, **kwargs):
            response = None
            _ = kwargs.get('_', None)
            url = kwargs.get('url', None) or args[0]
            if '_' in kwargs:
                kwargs.pop('_')
            error = False
            try:
                response = await func(*args, **kwargs)
            except Exception as e:
                error = True
                logging.error(msg=f'{_ + 1} 次 ({method})请求失败 请求地址({url}) \n 原因：{e}')
            finally:
                if not error:
                    if response is None:
                        if error:
                            logging.debug(msg=f'{_ + 1} 次 ({method})未请求 请求地址({url})')
                    else:
                        if response.status_code == 200:
                            logging.debug(msg=f'{_ + 1} 次 ({method})请求成功 请求地址({url})')
                            return self._parse(response, _=_ + 1)
                        else:
                            logging.debug(msg=f'{_ + 1} 次 ({method})请求失败({response.status_code}) 请求地址({url})')
                self.context.error_url.append(url)
                return response

        return warp

    @api.monitor(
        fields='_parse',
        ty=MONITOR_FUNC
    )
    def _success_response(
            self,
            response: Response
    ):
        return response

    def _request(
            self,
            urls: Union[str, List[str], Tuple[str]],
            is_async: bool = False,
            headers: Union[dict, None] = None,
    ):
        if headers is None:
            headers = self.context.headers
        _async_request = self.try_response_async(self._async_request)
        _normal_request = self.try_response(self._normal_request)
        if isinstance(urls, str):
            if is_async:
                asyncio.run(_async_request(urls, headers))
            else:
                _normal_request(urls, headers)
        elif isinstance(urls, Iterable):
            if is_async:
                loop = asyncio.get_event_loop()
                tasks = [_async_request(url, headers, _=_) for _, url in enumerate(urls)]
                loop.run_until_complete(asyncio.wait(tasks))
            else:
                for _, url in enumerate(urls):
                    _normal_request(url, headers, _=_)

    def _normal_request(
            self,
            url: str,
            headers: Union[str, dict]
    ) -> Response:
        self.context._url = url
        method = self.context._method
        response = None
        if method == 'GET':
            response = requests.get(url=url, headers=headers)
        elif method == 'POST':
            response = requests.post(url=url, headers=headers)
        return response

    async def _async_request(
            self,
            url: Union[str],
            headers: Union[dict, None]
    ) -> Response:
        self.context._url = url
        method = self.context._method
        async with httpx.AsyncClient(headers=headers) as client:
            response = None
            if method == 'GET':
                response = await client.get(url=url)
            elif method == 'POST':
                response = await client.post(url=url)
        return response

    def parse(
            self,
            response: Union[Response]
    ) -> Response:
        return response

    def urls(
            self
    ):
        return self.context.url

    def request(
            self,
            is_async: bool = False
    ) -> None:
        return self._request(urls=self.urls(), is_async=is_async)

    def _parse(
            self,
            response: Union[Response] = None,
            _: int = 0
    ) -> None:
        bi = BytesIO()
        if not response:
            response = self._return
        if hasattr(self, f'parse{_}'):
            res = eval(f'self.parse{_}(response)')
        else:
            res = self.parse(response)
        if isinstance(res, Iterable):
            for i, data in enumerate(res):
                path = f'datas/page-{_}/data_{i}.park'
                self.save(path, data)
        # self.items.update({
        #     f'{self._}': bi
        # })

    @api.monitor(
        'method',
        ty=MONITOR_VAR
    )
    def _method_upper(
            self
    ):
        self.context._method = self.context.method.upper()
