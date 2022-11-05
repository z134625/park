"""***********************************基础**************************"""

# 以下划线字母数字组成，并且只能以字母下划线开头，
# int, float, bool, str, list, tuple, set, dict
# "a" + "b", "a" * 2, *args 不定长参， （*， name）强制关键字传参， += 等价于 =  +


def year(y: int) -> str:
    """
    计算-传入的年份是闰年还是平年
    :param y:  传入年份为整形
    :return:  返回结果
    """
    if y % 4 == 0:
        if y % 100 == 0:
            if y % 400 == 0:
                return "闰年"
            return "平年"
        return "闰年"
    return "平年"


def get_phone(phone: str) -> tuple:
    """
    获取手机号前三位后四位值， 以及4到6位的值
    :param phone: 手机号字符串形式
    :return: 返回一个元组
    """
    three = phone[:3]
    four = phone[-4:]
    four_six = phone[3:6]
    return three, four, four_six


def get_name(info: str):
    """
    解析字符串中姓名性别年龄手机信息，并打印出
    :param info:  以姓名#性别#年龄#手机号格式
    :return:  返回信息字典
    """
    heard = ["姓名", "性别", "年龄", "手机号"]
    info = info.split("#")
    info_dict = {key: value for key, value in zip(heard, info)}
    for i in info_dict.keys():
        print(i + ":" + info_dict[i])


def sorted_number(numbers: list = None, reverse: bool = True) -> list:
    """
    用于排序数字
    :param numbers:  传入排序的列表
    :param reverse: True为降序， False 为升序
    :return: 原列表该操作在已有的列表上进行
    """
    if numbers is None:
        numbers = [1, 35, 2, 10, 23, 7, 66, 108, 45]
    numbers.sort(reverse=reverse)
    return numbers


def exclude(words: str, exclude_word: str) -> str:
    """
    用于排除字符串中指定的字母
    :param words:  原单词
    :param exclude_word:  排除的字母
    :return: 去除后的单词
    """
    word = " ".join(words.split(exclude_word))
    for i in word:
        print(i, end=" ")
    return word


def sandwich() -> None:
    """
    用与展示三明治的完成情况
    :return:
    """
    sandwich_orders = ["one", "two", "three"]
    finished_sandwiches = []
    for i in sandwich_orders:
        print(f"I made your tuna {i} sandwich")
        finished_sandwiches.append(i)

    for j in finished_sandwiches:
        print(f"finished tuna {j} sandwich")


def pastrami() -> None:
    """
    五香烟熏牛肉卖完了
    :return:
    """
    sandwich_orders = ["pastrami", "pastrami", "pastrami",
                       "pastrami", "one", "one", "one", "one", "one", "two", "two"]
    import random
    random.shuffle(sandwich_orders)
    print("熟食店的五香烟熏牛肉卖完了")
    length = sandwich_orders.__len__()
    n = 0
    while n < length:
        if sandwich_orders[n] == "pastrami":
            sandwich_orders = sandwich_orders.pop(n)
    finished_sandwiches = sandwich_orders
    if "pastrami" not in finished_sandwiches:
        print("ok'")
    else:
        print("error")


# def test1():
#     """"
#     >>> year(2012)
#     '闰年'
#     >>> year(1997)
#     '平年'
#     >>> get_phone("134567891010")
#     ('134', '1010', '567')
#     >>> get_name("Tom#男#22#134567891010")
#     姓名:Tom
#     性别:男
#     年龄:22
#     手机号:134567891010
#     >>> sorted_number(reverse=True)
#     [108, 66, 45, 35, 23, 10, 7, 2, 1]
#     >>> sorted_number(reverse=False)
#     [1, 2, 7, 10, 23, 35, 45, 66, 108]
#     >>> exclude(words="HANDCHINA", exclude_word="I")
#     H A N D C H   N A 'HANDCH NA'
#     >>> sandwich()
#     I made your tuna one sandwich
#     I made your tuna two sandwich
#     I made your tuna three sandwich
#     finished tuna one sandwich
#     finished tuna two sandwich
#     finished tuna three sandwich
#     >>> pastrami()
#     熟食店的五香烟熏牛肉卖完了
#     ok
#     """


a = 1
b = 2

a, b = b, a

c = a
a = b
b = c

"""***********************************函数**************************"""


def show_name(name: str) -> None:
    lower = name.lower()
    upper = name.upper()
    title = name.title()
    print(lower)
    print(upper)
    print(title)


def strip_name(name: str = '\nTom\t') -> None:
    print(name)
    print(name.lstrip())
    print(name.rstrip())
    print(name.strip())


def choice() -> None:
    people = ["one", "two", "three", "four"]
    people.insert(0, "开头")
    print(people)
    people.insert(people.__len__() // 2, "中间")
    print(people)
    people.append("最后")
    print(people)
    people.pop()
    print(people)
    people.clear()
    print(people)


def print_dict():
    d = {
        "pool": "池",
        "project": "项目",
    }
    for key, value in d.items():
        print(key + "\n\r", value)


def print_range():
    for i in range(1, 20, 2):
        print(i, end=",")


def get_3():
    print([eval(f"{i}**3") for i in range(0, 10)])


def keep(d: dict):
    return {
        key: value[:2]
        for key, value in d.items()
    }


def describe_city(city: tuple = ("New York", "BeiJing", "ShangHai"), country="China"):
    print(f"{city} is in {country}")


def make_album(singer, album, *number):
    return {
        "singer": singer,
        "album": album,
        "number": number if number else "未知",
    }


def make_car(car, version, **kwargs):
    return {
        "制造商": car,
        "型号": version, **kwargs
    }


def decor(func):
    def warp(*args, **kwargs):
        import datetime
        print(datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d %H:%M:%S"))
        print(func(*args, **kwargs))
        print(datetime.datetime.strftime(datetime.datetime.now(), "%a %b %d %H:%M:%S %Y"))
    return warp


@decor
def devide(a1, b1):
    try:
        return a1 / b1
    except ZeroDivisionError:
        return "ERROR"


# def test2():
#     """
#     >>> show_name("tom")
#     tom
#     TOM
#     Tom
#     """


"""***********************************函数**************************"""
# os  os.path.join()路径拼接 os.name 操作系统名 os.system 执行终端命令
# sys  sys.args 获取命令参数 sys.exit 推出程序
# time  time.time 获取当前时间戳 time.sleep 程序睡眠
# re  re.compile 生产正则表达式  re.sub 正则替换 re.split 正则切割
dic = {'yellow river': 'china', 'amazon river': 'brazil', 'nile': 'egypt'}

for key, value in dic.items():
    print(key.swapcase())
    print(value.swapcase())
    print(key + value)

infos = [("Tom", 12), ("Bob", 22)]
people = [{"姓名": i, "年龄": j} for i, j in infos]
print(people)

# if __name__ == '__main__':
#     import doctest
#
#     doctest.testmod()