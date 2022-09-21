import datetime
import re
def sum_number():
    sums = 0
    for i in range(1, 100 + 1):
        sums += i
    print(datetime.datetime.now(), end=':')
    print('module.sum_number')
    return sums

def sum_numbers(start, end):
    sums = 0
    for i in range(start, end + 1):
        sums += i
    return sums


class Sum:

    @staticmethod
    def sum_number():
        sums = 0
        for i in range(1, 100 + 1):
            sums += i
        print(datetime.datetime.now(), end=':')
        print('SUM')
        return sums