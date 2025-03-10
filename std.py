import threading
import time
from abc import ABC, abstractmethod

from cocoman.utils import Log

log = Log()


class StandardBarrageSpider(ABC):
    """标准弹幕爬虫"""

    def __init__(self, websocket=None):
        self.ws = websocket
        self.cached = []
        self.last_barrage_time = time.time()
        self.barrage_interval = 3

    async def process_message(self, ws, message: dict):
        """处理弹幕爬虫的消息"""
        if not message:
            await asyncio.sleep(0.5)
            return

        # 无脑发送即可
        if time.time() - self.last_barrage_time > self.barrage_interval:
            await self.send_to_slzb(ws, message)
            return

        # 需要进行去重
        if message not in self.cached:
            await self.send_to_slzb(ws, message)

    async def send_to_slzb(self, ws, one: dict):
        """给 SLZB 发送弹幕消息"""
        # await ws.send(json.dumps(one))
        log.success("已向 SLZB 发送消息 => {}".format(one))
        await asyncio.sleep(0.1)

        # 加入到全局弹幕
        self.cached.append(one)
        self.cached = self.cached[100:] if len(self.cached) > 200 else self.cached

        # 更新弹幕时间
        self.last_barrage_time = time.time()

    @abstractmethod
    def listen(self):
        """不停的监听弹幕"""
        pass

    @abstractmethod
    def pull(self):
        """从队列里取一个弹幕"""
        pass

    async def start(self):
        t = threading.Thread(target=self.listen)
        t.daemon = True
        t.start()
        while True:
            msg = self.pull()
            await self.process_message(self.ws, msg)


import queue
import random


class Test_STD_Spider(StandardBarrageSpider):
    q = queue.Queue()

    def listen(self):
        while True:
            v = random.randint(1, 5)
            log.info(f"生产 => {v}")
            self.q.put(v)
            time.sleep(random.randint(1, 3))

    def pull(self):
        try:
            msg = self.q.get(timeout=2)
            return msg
        except queue.Empty:
            log.warning("超时")


if __name__ == "__main__":
    import asyncio

    tss = Test_STD_Spider()
    asyncio.run(tss.start())
