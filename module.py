import re
def sum_number(start, end):
    sums = 0
    for i in range(start, end + 1):
        sums += i
    return sums

def sum_numbers(start, end):
    sums = 0
    for i in range(start, end + 1):
        sums += i
    return sums


class Sum:
    end = 100

    def sum_number(self, start):
        sums = 0
        for i in range(start, self.end + 1):
            sums += i
        return sums