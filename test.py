import datetime
from park.utils import park
from park.decorator import register, registers


# from park.conf.setting import setting, Date, Time, Cache


@register
def sum_number():
    sums = 0
    for i in range(1, 100 + 1):
        sums += i
    print(datetime.datetime.now(), end=':')
    print('this.sum_number')
    return sums


# @inherit(parent='Sum')
# class Aum:
#     def sums(self):
#         return self.end


if __name__ == '__main__':
    # setting.load('./config.json')
    import module

    registers(module, kwargs={'Sum': {'call': True}})
    park = park(exclude=park.EXCLUDE_SYS)
    print(park.tasks('sum_number',
                     kwargs={'sum_number': {
                                     'timing': datetime.datetime(year=2022, month=9, day=21, hour=11, minute=17, second=30)}}))
    # print(setting.note_time.value)
    # print(Aum().sum_number(1))
