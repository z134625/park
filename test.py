# from park.info.system import SYS
from park.utils import park
from park.decorator import register, registers
# from park.conf.setting import setting, Date, Time, Cache


@register
def sum_number(start, end):
    sums = 0
    for i in range(start, end + 1):
        sums += i
    return sums

# @inherit(parent='Sum')
# class Aum:
#     def sums(self):
#         return self.end


if __name__ == '__main__':
    # setting.load('./config.json')
    import module
    registers(module)
    park = park(exclude=park.EXCLUDE_SYS)
    park.task('Sum.sum_number')
    # print(setting.note_time.value)
    # print(Aum().sum_number(1))

