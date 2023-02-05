import asyncio
import logging
import os
import re
import httpx
import requests

from io import BytesIO
from decimal import Decimal
from httpx import Response

from collections.abc import (
    Iterable,
    Coroutine
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

from .paras import ToolsParas
from ...tools import listPath
from ...utils import api
from ...utils.base import ParkLY
from ...utils.api import (
    MONITOR_FUNC,
    MONITOR_VAR
)


class Tools(ParkLY):
    _name = 'tools'
    _inherit = ['monitor', 'command']
    paras = ToolsParas()

    def try_response(self,
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

    def try_response_async(self,
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

    @api.monitor(fields='_parse', ty=MONITOR_FUNC)
    def _success_response(self,
                          response: Response
                          ):
        return response

    def _request(self, urls: Union[str, List[str], Tuple[str]],
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

    def _normal_request(self,
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

    async def _async_request(self,
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

    def parse(self,
              response: Union[Response]
              ) -> Response:
        return response

    def urls(self):
        return self.context.url

    def request(self,
                is_async: bool = False
                ) -> None:
        return self._request(urls=self.urls(), is_async=is_async)

    def _parse(self,
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

    @api.monitor('method', ty=MONITOR_VAR)
    def _method_upper(self):
        self.context._method = self.context.method.upper()

    def number_to_chinese(self,
                          number: Union[int, float, str],
                          cash: bool = False
                          ) -> str:
        return self._number_to_chinese(number, cash)

    # 数字转中文主要方法
    def _number_to_chinese(self,
                           number: Union[int, float, str],
                           cash: bool
                           ) -> str:
        base = 10000
        base_number = str(Decimal(number))
        str_list = []
        chinese_number = []
        int_number = base_number
        float_number = '0'
        if '.' in base_number:
            int_number, float_number = base_number.split('.')
        int_number = int(int_number)
        float_number = float_number
        billion = False
        frequency = 1
        # 通过除以 base(10000) 将数字转化为四位
        while True:
            divisor = int_number // base
            remainder = int_number % base
            if divisor == 0:
                str_list.append(str(int_number))
                break
            str_list.append(str(remainder).rjust(4, '0'))
            frequency += 1
            res = pow(base, frequency)
            if billion:
                billion = False
                if str(res) in self.context.number_dict and res > pow(base, 2):
                    str_list.append(self.context.number_dict[str(res)])
                else:
                    str_list.append('亿')
            else:
                billion = True
                if str(res) in self.context.number_dict and res > pow(base, 2):
                    str_list.append(self.context.number_dict[str(res)])
                else:
                    str_list.append('万')

            int_number = divisor
        str_list = str_list[::-1]
        none = False
        for i, item in enumerate(str_list):
            if re.search(r'\d', item):
                c_s = self._thousands_chinese(item)
                if c_s == '零':
                    none = True
                    if len(str_list) == 1:
                        chinese_number.append(c_s)
                    continue
                elif chinese_number and not re.search(r'\d', chinese_number[-1]) and '仟' not in c_s:
                    chinese_number.append('零')
                chinese_number.append(c_s)
                none = False
            else:
                if none:
                    continue
                chinese_number.append(item)
        int_chinese = ''.join(chinese_number)
        float_chinese = self._float_chinese(float_number, cash)
        return int_chinese + float_chinese

    # 将四位数字转化为对应千分位中文读法
    def _thousands_chinese(self,
                           number: str
                           ) -> str:
        chinese_number = ''
        if number == '0000':
            return self.context.number_dict['0']
        if number == '0':
            return self.context.number_dict['0']
        if len(number) < 4:
            number = number.rjust(4, '0')
        if number[0] != '0':
            chinese_number += self.context.number_dict[number[0]] + self.context.number_dict['1000']
        if number[1] != '0' and number[2] != '0':
            chinese_number += self.context.number_dict[number[1]] + self.context.number_dict['100']
            chinese_number += self.context.number_dict[number[2]] + self.context.number_dict['10']
        elif number[1] != '0':
            chinese_number += self.context.number_dict[number[1]] + self.context.number_dict['100']
        elif number[2] != '0' and number[0] != '0':
            chinese_number += self.context.number_dict['0']
            chinese_number += self.context.number_dict[number[2]] + self.context.number_dict['10']
        elif number[2] != '0':
            chinese_number += self.context.number_dict[number[2]] + self.context.number_dict['10']
        if number[3] != '0' and not number[2] != '0' and (number[0] != '0' or number[1] != '0') and (
                number[1] == '0' or number[2] == '0'):
            chinese_number += self.context.number_dict['0']
        chinese_number += self.context.number_dict[number[3]] if number[3] != '0' else ''
        return chinese_number

    # 小数部分处理
    def _float_chinese(self,
                       number: str,
                       cash: bool
                       ) -> str:
        float_chinese = ''
        division = ''
        if number:
            division = '点' if not cash else '元'
            if int(number) == 0:
                if cash:
                    float_chinese += '元整'
                return float_chinese
            number = number.rstrip('0')
            for k, v in enumerate(number):
                float_chinese += self.context.number_dict[v]
                if k == 0 and cash:
                    float_chinese += '角'
                elif k == 1 and cash:
                    float_chinese += '分'
                    break
        return division + float_chinese

    @staticmethod
    def number_to_chinese_2(
            amount: Union[int, float, str]
    ) -> str:
        c_dict = {1: u'', 2: u'拾', 3: u'佰', 4: u'仟'}
        x_dict = {1: u'元', 2: u'万', 3: u'亿', 4: u'兆'}
        g_dict = {0: u'零', 1: u'壹', 2: u'贰', 3: u'叁', 4: u'肆', 5: u'伍', 6: u'陆', 7: '柒', 8: '捌', 9: '玖'}

        def number_split(number):
            g = len(number) % 4
            number_list = []
            lx = len(number) - 1
            if g > 0:
                number_list.append(number[0:g])
            k = g
            while k <= lx:
                number_list.append(number[k:k + 4])
                k += 4
            return number_list

        def number_to_capital(number):
            len_number = len(number)
            j = len_number
            big_num = ''
            for i in range(len_number):
                if number[i] == '-':
                    big_num += '负'
                elif int(number[i]) == 0:
                    if i < len_number - 1:
                        if int(number[i + 1]) != 0:
                            big_num += g_dict[int(number[i])]
                else:
                    big_num += g_dict[int(number[i])] + c_dict[j]
                j -= 1
            return big_num

        number = str(amount).split('.')
        integer_part = number[0]
        chinese = ''
        integer_part_list = number_split(integer_part)
        integer_len = len(integer_part_list)
        for i in range(integer_len):
            if number_to_capital(integer_part_list[i]) == '':
                chinese += number_to_capital(integer_part_list[i])
            else:
                chinese += number_to_capital(integer_part_list[i]) + x_dict[integer_len - i]
        if chinese and '元' not in chinese:
            chinese += '元'
        if chinese and len(number) == 1:
            chinese += '整'
        else:
            fractional_part = number[1]
            fractional_len = len(fractional_part)
            if fractional_len == 1:
                if int(fractional_part[0]) == 0:
                    chinese += '整'
                else:
                    chinese += g_dict[int(fractional_part[0])] + '角整'
            else:
                if int(fractional_part[0]) == 0 and int(fractional_part[1]) != 0:
                    chinese += '零' + g_dict[int(fractional_part[1])] + '分'
                elif int(fractional_part[0]) == 0 and int(fractional_part[1]) == 0:
                    chinese += '整'
                elif int(fractional_part[0]) != 0 and int(fractional_part[1]) != 0:
                    chinese += g_dict[int(fractional_part[0])] + '角' + g_dict[int(fractional_part[1])] + '分'
                else:
                    chinese += g_dict[int(fractional_part[0])] + '角整'
        return chinese