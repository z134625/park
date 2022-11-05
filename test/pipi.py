import datetime
import fas
from park.decorator import register, inherit
from park.decorator.timer import timer
from park.conf.setting import ParkConcurrency


@inherit(parent='PrintS', warn=True)
def printf():
    sum = 1
    for i in range(1, 1000):
        sum *= i
    return sum


@inherit(parent='PrintS', warn=True)
class Test:
    def __init__(self, msg):
        self.msg = msg

    def printf(self):
        print(2)
# @timer(msg='park')
# def main(a=1):
#     print(a)
#     # pool = Pool(60)
#     for i in range(10000):
#         pip()
    #     pool.apply_async(pip)
    # pool.close()
    # pool.join()
    # ParkConcurrency.start()


if __name__ == '__main__':
    # main()
    from park import park
    # print(park['printf'][0]())
    # print(park['PrintS'].printf(1))
    # print(Test(123).printf())
    # s = dir(fas)
    # print(fas.__name__)
    # index = s.index('__builtins__')
    # print(s[:index])
    print(park['printf__app'].app)
    print(park['printf'])
    # for i in park['printf__app']:
    #     print(i.app)
