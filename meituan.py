import threading
import time
from queue import Queue

from loguru import logger
from requests import Session

session = Session()
default_headers = {
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0",
}
session.headers.update(default_headers)


class MeituanListener:
    msg_queue = Queue()
    items = []

    def get_liveid(self, short_url: str) -> str:
        resp = session.get(short_url, allow_redirects=False)
        new_url = resp.headers["Location"]
        logger.info("{} => {}".format(resp.status_code, new_url))
        liveid = new_url.split("liveid=")[1].split("&")[0]
        logger.info("已获取到liveid为{}".format(liveid))
        return liveid

    def add_msg(self, liveid: str):
        url = "https://i.meituan.com/mapi/dzu/live/livestudiobaseinfo.bin?"
        params = {
            "platform": "2",
            "appid": "10",
            "inapp": "false",
            "liveid": liveid,
            "anchorId": "0",
            "sharekey": "B3053BB78F172E06BEA628B879C4FDC7",
            "access_source": "",
            "invokeApp": "",
            "yodaReady": "h5",
            "csecplatform": "4",
            "csecversion": "2.4.0",
        }
        resp = session.get(url, params=params, timeout=10)
        jsdata = resp.json()
        try:
            msgs = jsdata["messageVO"]["msgs"]
            if not msgs:
                logger.warning("直播间：{} | 无弹幕数据".format(liveid))
                return
        except:
            logger.warning(resp.text)
            return

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
                # print("[聊天] {}（{}）：{}".format(username, uid, content))
                self.msg_queue.put(item)

    def listen(self, liveid: str = None, short_url: str = None):
        assert liveid or short_url, "无目标源"
        liveid = liveid or self.get_liveid(short_url)
        times = 0
        while True:
            self.add_msg(liveid)
            time.sleep(3)
            times += 1
            # print("\r已访问{}次".format(times), flush=True, end='')

    def get_msg(self):
        try:
            return self.msg_queue.get(timeout=10)
        except:
            pass


def test():
    short_url = "http://dpurl.cn/voNM8RIz"
    liveid = "9115262"
    liveid = "9050450"
    MeituanListener().listen(liveid)


def test2():
    liveid = "9162660"
    meituan_listener = MeituanListener()
    t1 = threading.Thread(target=meituan_listener.listen, args=(liveid,))
    t1.start()

    while True:
        item = meituan_listener.get_msg()
        if item:
            logger.info(item)


if __name__ == "__main__":
    test2()
