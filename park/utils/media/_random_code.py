import random


class Code:
    """
    验证码生成类
    支持纯字母，纯数字， 字母数字混合， 公式算数， 自定义内容
    """
    def __init__(self, class_: str = 'blend', length: int = 4, is_case: bool = False, **kwargs):
        self.mode = class_
        self.length = length
        assert self.length < 10, "不允许生成的验证码过长"
        self.is_case = is_case
        self.dict_ = kwargs.get('words', {})
        assert isinstance(self.dict_, dict), "自定义验证码必须为字典形式"

    def _words_library(self):
        lower = "abcdefghijklmnopqrstuvwxyz"
        upper = lower.upper()
        numbers = '1234567890'
        symbol = '+-*'
        if self.mode == 'operation':
            one = random.sample(numbers, 1)[0]
            two = random.sample(numbers, 1)[0]
            sy = random.sample(symbol, 1)[0]
            formula = "%s %s %s" % (one, sy, two)
            result = eval(formula)
        elif self.mode == 'number':
            formula = "".join(random.sample(numbers, self.length))
            result = formula
        elif self.mode == 'letter':
            formula = "".join(random.sample(lower + upper, self.length))
            if self.is_case:
                result = formula
            else:
                result = formula.lower()
        elif self.mode == 'custom':
            formula = "".join(random.sample(self.dict_.keys(), 1))
            if self.is_case:
                result = self.dict_[formula]
            else:
                result = self.dict_[formula].lower()
        else:
            formula = "".join(random.sample(lower + upper + numbers, self.length))
            if self.is_case:
                result = formula
            else:
                result = formula.lower()
        return formula, result

    def generator(self):
        return self._words_library()

