#!/usr/bin/env python

# -*- coding: utf-8 -*-

import random

# 定义一个函数，用于生成一个随机数

def random_number():

    return random.randint(1, 100)

# 定义一个函数，用于比较玩家猜测的数字和随机数的大小

def compare_number(num1, num2):

    if num1 > num2:

        print('猜大了')

    elif num1 < num2:

        print('猜小了')

    else:

        print('恭喜你，猜对了！')

# 生成一个随机数

random_num = random_number()

# 玩家猜测的次数

count = 0

# 开始游戏

print('游戏开始，请猜一个1-100之间的数字：')

# 循环猜测，直到猜对为止

while True:

    count += 1

    player_num = int(input())

    compare_number(player_num, random_num)

    if player_num == random_num:

        break

# 游戏结束，打印结果

print('你一共猜了%d次' % count)

