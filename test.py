# import datetime
# import time
#
# from park.decorator import register, registers, park, Park, inherit
# from park.web.park import ParkWeb
# from park.decorator.encryption import encryption, EncryptionData
#
# # from park.conf.setting import setting, Date, Time, Cache
# web = ParkWeb()
# import module
#
# aum = registers([module], kwargs='./co.json')
#
# @register
# def sum_number():
#     for i in range(11111110):
#         pass
#     return 1+1
#
#
# @inherit(parent='Sum', register=False)
# class Aum:
#     end = 1000
#
#     @encryption(mode=2)
#     def sums(self):
#         return self.end


if __name__ == '__main__':
    # setting.load('./config.json')

    # print(park['Aum'])
    # # park(exclude=park.EXCLUDE_SYS)
    # print(park['sum_numbers'](1, 100))
    # a = park.tasks(['sum_number', 'sum_numbers', 'sums'],
    #                kwargs='./config.json')
    # print(a)
    # k = Park()
    #
    # print(park.all)
    # print(k.all)
    # print(park['_Configs'])
    # print(park['sums'])
    # class NewNone(type):
    #
    #     @classmethod
    #     @property
    #     def __module__(mcs):
    #         return 'this'
    #
    # print(NewNone)
    # sk = park['_ProgressPark']
    # with sk(10) as s:
    #     for i in range(10):
    #         s(func=sum_number)
    from park.ai import FixedInvestmentCalculator as fx, REINSTATEMENT, YearField, Reta, LOW, MEDIUM, HIGH, MonthField
    _a = 0
    s = Reta(HIGH)
    fx = fx(earning_rate=s, interval_amount=5000,
            principal=1000, dividend=REINSTATEMENT, fixed=MonthField(31))
    fx.calculator()
    print(fx.amount)
    print(fx.profit)
    print(fx.principal)
