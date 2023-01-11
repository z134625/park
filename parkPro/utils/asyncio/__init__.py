import asyncio
import time


def times(func):
    def warp(*args, **kwargs):
        start = time.time()
        res = func(* args, ** kwargs)
        end = time.time()
        print(round(end - start, 6))
        return res
    return warp


async def normal1():
    j = 0
    for i in range(10000000):
        j += i
    return j


async def normal2():
    j = 0
    for i in range(10000000):
        j += i
    return j


async def normal3():
    j = 0
    for i in range(10000000):
        j += i
    return j


def nor():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop=loop)
    task = [eval(f'normal{i}()') for i in range(1, 4)]

    res = loop.run_until_complete(asyncio.wait(task))
    return res


@times
def print1():
    print(nor())


if __name__ == '__main__':
    # 149999985000000
    # 1.301302
    print1()
    