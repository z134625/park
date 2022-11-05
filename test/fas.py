from park import park
from park.decorator import register


@register(call=True, arg=(1, 2))
def printf(a, b):
    return a + b


@register(call=True)
class PrintS:
    def __init__(self):
        pass

    def printf(self):
        print(1)


if __name__ == '__main__':
    res = park['PrintS']
    print(park['printf'])
    print(res.printf())
