import datetime
import json
import threading
import time
from abc import ABC, abstractmethod

from cocoman.utils import Log

log = Log()


class StandardBarrageSpider(ABC):
    """标准弹幕爬虫"""

    def __init__(self, barrs=None, websocket=None):
        self.websocket = websocket
        self.barrs = barrs

    @abstractmethod
    def listen(self):
        """从美团不停的监听弹幕"""
        pass

    @abstractmethod
    def pull_msg(self):
        """从队列里取一个弹幕"""
        pass

    async def start(self):
        t = threading.Thread(target=self.listen)
        t.daemon = True
        t.start()
        while True:
            spider_msg = self.pull_msg()
            if not spider_msg:
                await asyncio.sleep(0.2)
                continue
            log.success(f"从队列取出  ==>  {spider_msg}")
            if not self.barrs:
                continue
            self.barrs = self.barrs[100:] if len(self.barrs) > 200 else self.barrs
            if spider_msg not in self.barrs:
                self.barrs.append(spider_msg)
                if not self.websocket:
                    continue
                await self.websocket.send(json.dumps(spider_msg))
                print(f"{datetime.datetime.now()}\t已向前端发送消息\n{spider_msg}\n")
                await asyncio.sleep(0.2)


import queue
import random


class Test(StandardBarrageSpider):
    q = queue.Queue()

    def listen(self):
        while True:
            v = random.randint(1, 10000)
            log.info(f"{v} <= 生产")
            self.q.put(v)
            time.sleep(random.randint(1, 3))

    def pull_msg(self):
        try:
            msg = self.q.get(timeout=1)
            return msg
        except queue.Empty:
            log.warning("超时")


if __name__ == "__main__":
    import asyncio

    t = Test()
    asyncio.run(t.start())
