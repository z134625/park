import datetime
import re
from park.conf import exists_rename

def sum_number(w):
    print(w)


def sum_numbers(start, end):
    sums = 0
    for i in range(start, end + 1):
        sums += i
    return sums


class Sum:
    end = 100

    @staticmethod
    def sum_number(k):
        print(k)

    def sums(self):
        return self.end


del re
del datetime

a = lambda method: setattr(method, '_onchange', 'sum') or method

class GroupBy(object):

    def __init__(self, obj, key=None):
        # assert isinstance(obj, Iterable)
        val = None
        group_dict = {}
        for item in obj:
            if key is None:
                group_dict.update({
                    str(item): group_dict.get(str(item), []) + [item]
                })
            elif key is True:
                if item == val:
                    group_dict.update({
                        str(item): group_dict.get(str(item), []) + [item]
                    })
                    val = item
                else:
                    if str(item) not in group_dict:
                        group_dict.update({
                            str(item): [item]
                        })
                    else:
                        group_dict.update({
                            exists_rename(str(item), paths=group_dict.keys(), dif=True): [item]
                        })
                    val = item
            elif callable(key):
                group_dict.update({
                    str(key(item)): group_dict.get(str(key(item)), []) + [item]
                })

        self.group_list = list(group_dict.items())
        self._length = len(self.group_list)
        self._iter = 0

    def __iter__(self):
        return self

    def __next__(self):
        obj = self.group_list
        self._iter += 1
        if self._iter > self._length:
            raise StopIteration
        else:
            return obj[self._iter - 1]


sd = GroupBy([('a', 1), ('a', 1), ('b', 2), ('c', 1), ('a', 1), ('c', 1), ('a', 1)], key=True)

for i in sd:
    print(i)



