import datetime
from park.utils import park
from park.decorator import register, registers
from park.web.park import ParkWeb

# from park.conf.setting import setting, Date, Time, Cache
web = ParkWeb()
@register
def sum_number(a):
    print(a)

# @inherit(parent='Sum')
# class Aum:
#     def sums(self):
#         return self.end
if __name__ == '__main__':
    # setting.load('./config.json')
    import module
    registers(module, kwargs={'Sum': {'call': True}})
    park = park()
    print(park.all)
    print(park[1])
    print(park.tasks(['sum_number', 'sum_numbers'],
                     kwargs={
                         'args': 1,
                         'this': {
                             'args': {
                                 'a': 'dd'
                             }
                         },
                         'module.Sum': {
                             'args': 'pp',
                             'timing': datetime.datetime(2022, 9, 26, 20, 30, 00)
                         },
                         'module.sum_numbers': {
                             'args': (1, 100)
                         }
                     }))
    # print(setting.note_time.value)
    # print(Aum().sum_number(1))
