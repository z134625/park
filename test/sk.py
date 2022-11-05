import datetime
import os
import sys
import time

from park.conf.setting import ParkConcurrency, RealTimeUpdate, ParkQueue
from park.utils.media.tools import code


def sender(extend):
    print(f"发送(recipient){datetime.datetime.now()}")
    extend.send("myname1", recv="recipient")
    time.sleep(2)
    print(f"发送(recipient1){datetime.datetime.now()}")
    extend.send("myname2", recv="recipient1")
    time.sleep(2)
    # print(f"发送(recipient2){datetime.datetime.now()}")
    # extend.send("myname3", recv="recipient6")


def recipient(extend):
    msg = extend.recv(timeout=8)
    if msg:
        print(f"进程2接收到的消息({datetime.datetime.now()})：", end="")
        print(msg)


def recipient1(extend):
    msg = extend.recv(timeout=8)
    if msg:
        print(f"进程3接收到的消息({datetime.datetime.now()})：", end="")
        print(msg)


def recipient2(extend):
    msg = extend.recv(timeout=8)
    if msg:
        print(f"进程4接收到的消息({datetime.datetime.now()})：", end="")
        print(msg)


def recipient3(extend):
    msg = extend.recv(timeout=8)
    if msg:
        print(f"进程5接收到的消息({datetime.datetime.now()})：", end="")
        print(msg)


def recipient4(extend):
    msg = extend.recv(timeout=8)
    if msg:
        print(f"进程6接收到的消息({datetime.datetime.now()})：", end="")
        print(msg)


def recipient5(extend):
    msg = extend.recv(timeout=8)
    if msg:
        print(f"进程7接收到的消息({datetime.datetime.now()})：", end="")
        print(msg)


def recipient6(extend):
    msg = extend.recv(timeout=8)
    if msg:
        print(f"进程8接收到的消息({datetime.datetime.now()})：", end="")
        print(msg)


def Concurrency():
    extend = ParkQueue()
    ParkConcurrency.addProcess(sender, extend)
    ParkConcurrency.addProcess(recipient, extend)
    ParkConcurrency.addProcess(recipient1, extend)
    # ParkConcurrency.addProcess(recipient2, extend)
    # ParkConcurrency.addProcess(recipient3, extend)
    # ParkConcurrency.addProcess(recipient4, extend)
    # ParkConcurrency.addProcess(recipient5, extend)
    # ParkConcurrency.addProcess(recipient6, extend)
    ParkConcurrency.start()
    extend.del_cache()


if __name__ == '__main__':
    p = RealTimeUpdate(func=Concurrency)
    p.start()
