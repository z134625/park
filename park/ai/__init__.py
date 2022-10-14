import random
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta

__doc__ = """
当配置文件选择frame 选择pytorch 是将有
  Loss，  ：Loss(output, target, loss) 配置文件提供loss 输入loss 默认从配置读取也可设置
  Weight， ：Weight (net, lr, momentum, optimS) net必选为输入网络 lr 默认0.01 ，momentum 默认0.9也可从配置文件读取，
                                                optimS默认从配置文件读取也可指定
  program、 ：program()将保存模型 program.load()将加载已有模型
"""
CASH = 0
REINSTATEMENT = 1
LOW = 0
MEDIUM = 1
HIGH = 2


class Reta:
    def __init__(self, risk):
        self.risk_grade = risk

    def _generate_rates(self):
        less_rate = [0.01, 0.02, -0.01, -0.02] * 10
        middle_rate = [0.04, 0.05, -0.04, -0.05] * 10
        more_rate = [0.08, 0.09, -0.08, -0.09] * 10
        res_rate_0 = self._get_rates(less_rate, [100, 80, 90, 70])
        res_rate_1 = self._get_rates(middle_rate, [100, 80, 90, 70])
        res_rate_2 = self._get_rates(more_rate, [100, 80, 90, 70])
        res_rate = self._get_rates(res_rate_0 * 2 + res_rate_1 * 2 + res_rate_2 * 2, [5])
        if self.risk_grade == 0:
            res_rate += res_rate_0 * 3
        elif self.risk_grade == 1:
            res_rate += res_rate_1 * 3
        elif self.risk_grade == 2:
            res_rate += res_rate_2 * 3
        res_rate += [0.01, 0.02, -0.01, -0.02] * 50 + [0] * 500
        return res_rate

    @staticmethod
    def _get_rates(rates, nums):
        res = []
        for i in random.sample(rates, random.sample([4, 5, 6], 1)[0]):
            res += [i] * random.sample(nums, 1)[0]
        return res

    @property
    def value(self):
        res = self._generate_rates()
        random.shuffle(res)
        return res

    @property
    def month_rate(self):
        if self.risk_grade == 0:
            return random.sample([0.03, 0.02, 0.01], 1)[0]
        elif self.risk_grade == 1:
            return random.sample([0.06, 0.07, 0.08], 1)[0]
        elif self.risk_grade == 2:
            return random.sample([0.10, 0.11, 0.12], 1)[0]

    @property
    def year_rate(self):
        if self.risk_grade == 0:
            return random.sample([0.06, 0.05, 0.04], 1)[0]
        elif self.risk_grade == 1:
            return random.sample([0.1, 0.15, 0.2], 1)[0]
        elif self.risk_grade == 2:
            return random.sample([0.3, 0.4, 0.5], 1)[0]


class Amount:
    pass


class Field:
    def __init__(self, value, field_type):
        self.value = value
        self.field_type = field_type


class DateField(Field):
    def __init__(self, value, key=None):
        super(DateField, self).__init__(value, 'Date')
        self.sign = key

    def divide(self, field):
        pass

    def items(self):
        return relativedelta(**{
            self.sign: self.value
        })


class YearField(DateField):

    def __init__(self, value):
        super(YearField, self).__init__(value, 'years')


class MonthField(DateField):

    def __init__(self, value):
        super(MonthField, self).__init__(value, 'months')


class FixedInvestmentCalculator:

    def __init__(self, earning_rate=0.0,
                 fixed=YearField(value=1), interval=MonthField(value=1),
                 interval_amount=1000,
                 dividend=CASH,
                 principal=0):
        self.amount = 0
        self.profit = 0
        self.earning_rate = earning_rate
        self._earning_rate = earning_rate
        self.fixed = fixed
        self._fixed = fixed
        self.interval = interval
        self._interval = interval
        self.interval_amount = interval_amount
        self._interval_amount = interval_amount
        self.dividend = dividend
        self._dividend = dividend
        self.principal = principal
        self._principal = principal
        self.rate = None

    def init(self):
        self.amount = 0
        self.profit = 0
        self.earning_rate = self._earning_rate
        self.fixed = self._fixed
        self.interval = self._interval
        self.interval_amount = self._interval_amount
        self.dividend = self._dividend
        self.principal = self._principal
        if isinstance(self.earning_rate, (float, int)):
            self.rate = (self.earning_rate / 365)
            self.month_rate = (self.earning_rate / 12)
            self.year_rate = self.earning_rate
        elif isinstance(self.earning_rate, (list, tuple)):
            self.rate = self._get_random_rate
            self.month_rate = self._get_random_rate
            self.year_rate = self._get_random_rate
        elif isinstance(self.earning_rate, Reta):
            self.earning_rate = self.earning_rate.value
            self.rate = self._get_random_rate
            self.month_rate = self.earning_rate.month_rate
            self.year_rate = self.earning_rate.year_rate
        # self.frequency = self.fixed.divide(self.interval)

    def _get_random_rate(self):
        return random.sample(self.earning_rate, 1)[0]

    def calculator(self):
        self.init()
        return self._calculator()

    def _calculator(self):
        now = date.today()
        day = timedelta(days=1)
        days = 0
        calculation_date = now
        interval = now + self.interval.items()
        end = now + self.fixed.items()
        self.amount = self.principal
        month_amount = self.amount
        month_profit = self.profit
        while True:
            rate = (self.earning_rate if isinstance(self.earning_rate, (float, int)) else self.rate())
            if calculation_date >= end:
                break
            if calculation_date == interval:
                self.amount += self.interval_amount
                self.principal += self.interval_amount
                interval += self.interval.items()
            profit = self.amount
            if self.dividend:
                self.amount += self.amount * rate
            else:
                self.amount += self.principal * rate
            self.profit += self.amount - profit
            calculation_date += day
            days += 1
            if days % 30 == 0:
                profit = month_amount
                if self.dividend:
                    month_amount += month_amount * rate
                else:
                    month_amount += self.principal * rate
                month_profit += month_profit - profit
            elif