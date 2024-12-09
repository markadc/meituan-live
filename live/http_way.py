import time

from loguru import logger
from wauo import WauoSpider


class MeituanListener:
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

    def get_msg(self, liveid: str):
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
        msgs = jsdata["messageVO"]["msgs"]
        if not msgs:
            logger.warning("直播间：{} | 无弹幕数据".format(liveid))
        for one in jsdata["messageVO"]["msgs"][::-1]:
            username = one["imUserDTO"]["userName"]
            content = one["imMsgDTO"]["content"]
            item = "{}：{}".format(username, content)
            if item not in self.items:
                self.items.append(item)
                print(item)

    def listern_live(self, liveid: str = None, short_url: str = None):
        assert liveid or short_url, "无目标源"
        liveid = liveid or self.get_liveid(short_url)
        while True:
            self.get_msg(liveid)
            time.sleep(3)


def test():
    short_url = "http://dpurl.cn/voNM8RIz"
    liveid = "9050450"
    MeituanListener().listern_live(liveid)


if __name__ == "__main__":
    test()
