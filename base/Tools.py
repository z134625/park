import re
from decimal import Decimal
from typing import (
    Union,
)

from .paras import ToolsParas
from ..utils.base import ParkLY


class Tools(ParkLY):
    _name = 'tools'
    _inherit = ['monitor', 'command']
    paras = ToolsParas()

    def number_to_chinese(
            self,
            number: Union[int, float, str],
            cash: bool = False
    ) -> str:
        return self._number_to_chinese(number, cash)

    # 数字转中文主要方法
    def _number_to_chinese(
            self,
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
    def _thousands_chinese(
            self,
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
    def _float_chinese(
            self,
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
