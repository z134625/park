import asyncio
import websockets
import random


dic_send = 2

"""实现一直给客户端发消息，异步等待3秒，达到特定要求给客户端发送"""


async def echo(websocket, path):
    cnt = 0
    while True:
        x = random.randint(1, 100)
        if x == dic_send:
            cnt += 1
            await websocket.send(str(cnt) + ": " + str(dic_send))  # 第几个2传过来
        print(x)
        await asyncio.sleep(3)


start_server = websockets.serve(echo, '127.0.0.1', 5678)  # 地址改为你自己的地址
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
