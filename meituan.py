import threading
import time
from queue import Queue

from loguru import logger
from wauo import WauoSpider
from wauo.utils import cprint


class MeituanListener:
    msg_queue = Queue()

    def __init__(self):
        self.req = WauoSpider()
        self.items = []

    def get_liveid(self, short_url: str) -> str:
        resp = self.req.send(short_url, allow_redirects=False)
        new_url = resp.headers["Location"]
        logger.info("{} => {}".format(resp.status_code, new_url))
        liveid = new_url.split("liveid=")[1].split("&")[0]
        logger.info("已获取到liveid为{}".format(liveid))
        return liveid

    def push(self, liveid: str):
        url = "https://i.meituan.com/mapi/dzu/live/livestudiobaseinfo.bin?"
        params = {
            "platform": "2",
            "appid": "10",
            "inapp": "false",
            "liveid": liveid,
            "anchorId": "0",
            "sharekey": "EC342B53CC509B564BDAA0261A7006E2",
            "access_source": "",
            "invokeApp": "",
            "yodaReady": "h5",
            "csecplatform": "4",
            "csecversion": "2.4.0",
        }
        resp = self.req.send(url, params=params)
        jsdata = resp.json()
        for one in jsdata["messageVO"]["msgs"][::-1]:
            username = one["imUserDTO"]["userName"]
            uid = one["imUserDTO"]["userId"]
            content = one["imMsgDTO"]["content"]
            item = dict(
                type="ChatMessage",
                name=username,
                uid=uid,
                head_img="",
                content=content,
            )
            if item not in self.items:
                self.items.append(item)
                logger.info("[聊天] {}（{}）：{}".format(username, uid, content))
                self.msg_queue.put(item)

    def listener(self, liveid: str = None, short_url: str = None):
        assert liveid or short_url, "无目标源"
        liveid = liveid or self.get_liveid(short_url)
        times = 0
        while True:
            self.push(liveid)
            time.sleep(3)
            times += 1
            # cprint("已访问{}次".format(times))
            print("\r已访问{}次".format(times), flush=True, end='')

    def pull(self):
        try:
            return self.msg_queue.get(timeout=60)
        except Exception as e:
            logger.error(type(e))


def test():
    short_url = "http://dpurl.cn/voNM8RIz"
    liveid = "9115262"
    liveid = "9050450"
    MeituanListener().listener(liveid)


def test2():
    liveid = "9050450"
    meituan_listener = MeituanListener()
    t1 = threading.Thread(target=meituan_listener.listener, args=(liveid,))
    t1.start()

    while True:
        item = meituan_listener.pull()
        if item:
            logger.warning(item)


if __name__ == "__main__":
    test2()
