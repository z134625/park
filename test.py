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

    @encryption(mode=2)
    def sums(self):
        return self.end


if __name__ == '__main__':
    # setting.load('./config.json')
    import module

    aum = registers([module, Aum], kwargs='./co.json')
    print(aum.sums__parent())
    park(exclude=park.EXCLUDE_SYS)
    print(park['sum_numbers'](1, 100))
    a = park.tasks(['sum_number', 'sum_numbers', 'sums'],
                   kwargs='./config.json')
    print(a)
    k = Park()

    print(park.all)
    print(k.all)
