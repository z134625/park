import datetime
from park.decorator import register, registers, park, Park
from park.web.park import ParkWeb
from park.decorator.encryption import encryption, EncryptionData
# from park.conf.setting import setting, Date, Time, Cache
web = ParkWeb()


@register
def sum_number(a):
    print(a)


class Aum:
    end = 1000

    def __init__(self, num, key):
        pass

    @encryption(mode=2)
    def sums(self):
        return self.end


if __name__ == '__main__':
    # setting.load('./config.json')
    import module
    aum = registers([module, Aum], kwargs='./co.json')[0]
    res = aum.sums()
    print(res)
    # a = park(exclude=park.EXCLUDE_DEFAULT)
    print(park['sum_numbers'](1, 100))
    print(park.tasks(['sum_number', 'sum_numbers'],
                     kwargs='./config.json'))
    k = Park()

    print(k.all)
    print(park.all)
