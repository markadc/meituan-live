import json
import random
import threading
import time
from datetime import datetime
from functools import partial
from queue import Queue

import requests
from wauo.utils import Loger, cprint

log = Loger()

ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0"
default_headers = {"upgrade-insecure-requests": "1", "user-agent": ua}
session = requests.Session()
session.headers.update(default_headers)

red = partial(cprint, color="red")
timef = lambda ts: datetime.fromtimestamp(ts / 1000).strftime("%Y-%m-%d %H:%M:%S")


class MeituanSpider:
    """美团爬虫"""

    def __init__(self):
        self.msg_queue = Queue()
        self.unq_msgs = []
        self.__anchor_id = None
        self.__anchor_name = None
        self.__live_id = None

    def ensure_cookie(self, cookie: str):
        self.cookie = cookie
        self.headers = {"User-Agent": ua, "Cookie": cookie}

    def start_live(self, live_id=None):
        """开播"""
        live_id = live_id or self.crawl_plan_live_ids()[0]
        url = f"https://mlive.meituan.com/live/centercontrol/component/liveadmin/startlive?liveid={live_id}&appid=10&yodaReady=h5&csecplatform=4&csecversion=2.4.0"
        res = requests.get(url, headers=self.headers)
        red("{}  {}".format(live_id, res.text))

    def stop_live(self):
        """关播"""
        url = f"https://mlive.meituan.com/live/centercontrol/component/liveadmin/stoplive?liveid={self.live_id}&appid=10&yodaReady=h5&csecplatform=4&csecversion=2.4.0"
        res = requests.get(url, headers=self.headers)
        red(res.text)

    @property
    def anchor_id(self) -> str:
        if self.__anchor_id:
            return self.__anchor_id
        url = 'https://mlive.meituan.com/live/centercontrol/login/permissioncheck?liveid=&appid=10&yodaReady=h5&csecplatform=4&csecversion=2.4.0'
        resp = session.get(url, headers=self.headers)
        self.__anchor_id = resp.json()["data"]["anchorId"]
        return str(self.__anchor_id)

    @property
    def live_id(self) -> str:
        if self.__live_id:
            return self.__live_id
        self.__live_id = self.crawl_curr_live_id()
        return self.__live_id

    @live_id.setter
    def live_id(self, value):
        self.__live_id = value

    @property
    def anchor_name(self) -> str:
        if self.__anchor_name:
            return self.__anchor_name
        url = f"https://mlive.meituan.com/api/mlive/anchor/appanchorinfo.bin?anchorid={self.anchor_id}&usertype=2&appid=10&yodaReady=h5&csecplatform=4&csecversion=2.4.0"
        resp = session.get(url, headers=self.headers)
        self.__anchor_name = resp.json()["data"]["anchorName"]
        return str(self.__anchor_name)

    def crawl_plan_live_ids(self):
        url = f"https://mlive.meituan.com/api/mlive/anchor/apppagelives.bin?playstatus=1&anchorid={self.anchor_id}&usertype=2&start=0&limit=10&appid=10&yodaReady=h5&csecplatform=4&csecversion=2.4.0"
        resp = session.get(url, headers=self.headers)
        jsonData = resp.json()
        live_ids = [item["liveId"] for item in jsonData["data"]]
        if len(live_ids) == 0:
            log.warning("{}（{}） | 无直播计划".format(self.anchor_name, self.anchor_id))
        return live_ids

    def crawl_curr_live_id(self):
        """获取当前正在直播的id"""
        url = f"https://mlive.meituan.com/live/centercontrol/liveinfo?anchorId={self.anchor_id}&appid=10&yodaReady=h5&csecplatform=4&csecversion=2.4.0"
        i = 0
        while True:
            mark = None
            try:
                res = session.get(url, headers=self.headers)
                mark = res.text
                jsonData = res.json()
                if not jsonData["data"]:
                    log.warning("无直播计划也无直播")
                    time.sleep(3)
                    continue
                live_status = jsonData["data"]["liveMetaStatus"]["liveStatus"]
                if live_status == 1:
                    log.warning("当前只有直播计划，但是未开播")
                    time.sleep(3)
                    continue
                trueBeginTime = jsonData["data"]["trueBeginTime"]
                live_id = jsonData["data"]["liveId"]
                log.info("美团直播间id：{}  实际开播时间：{}".format(live_id, trueBeginTime))
                self.__live_id = str(live_id)
                return str(live_id)
            except Exception as e:
                log.error("{}  {}".format(e, mark))
                time.sleep(5)
            finally:
                i += 1
                if i >= 200:
                    raise Exception("监听账号达到上限")

    @staticmethod
    def get_live_id(short_url: str):
        """从APP端分享的短URL地址获取live_id"""
        resp = session.get(short_url, allow_redirects=False)
        new_url = resp.headers["Location"]
        log.info("{} => {}".format(resp.status_code, new_url))
        live_id = new_url.split("liveid=")[1].split("&")[0]
        log.info("已获取到 liveid 为{}".format(live_id))
        return str(live_id)

    def crawl_goods(self, live_id: str = None):
        """默认抓取当前直播的商品"""
        live_id = live_id or self.live_id
        headers = {
            "Content-Type": "application/json",
            "startTime": str(time.time() * 1000),
            "Cookie": self.cookie,
            "User-Agent": ua,
        }
        params = {
            "appid": "10",
            "yodaReady": "h5",
            "csecplatform": "4",
            "csecversion": "2.4.0"
        }
        data = {
            "liveId": live_id,
            "paramBody": "{\"liveid\":%s,\"requestType\":3,\"recallCondition\":{\"hidden\":false,\"needAllGoods\":false,\"query\":\"\",\"needGoodsSecKillType\":true,\"needAuditFailureReasons\":true,\"needDiagnosticTag\":true},\"goodShelfType\":1,\"containsDeletedAndSubForbid\":false,\"mainCityId\":null,\"requestSource\":1,\"pageSource\":9,\"needShopStatisticalInfo\":true,\"enableAnchorPage\":true,\"pageParam\":{\"pageNum\":1,\"pageSize\":100},\"extraInfo\":{\"consoleRequestScene\":1}}" % live_id,
            "appid": "10"
        }
        url = "https://i.meituan.com/mapi/dzu/live/goods/goodslisttob.bin"
        resp = session.post(url, headers=headers, params=params, json=data)
        jsonStr = resp.text
        print("{}（直播间id）的商品信息如下".format(live_id))
        jsonData = json.loads(jsonStr)
        assert jsonData["code"] == 0, jsonStr
        ggs = []
        for one in jsonData["data"]["goodsList"]:
            goods_id = one["goodsId"]
            goods_type_id = one["goodsType"]
            title = one["titleInfo"]["title"]
            market_price = one["goodsPriceInfo"]["marketPrice"]
            discount = one["goodsPriceInfo"]["discount"]
            sale_price = one["goodsPriceInfo"]["salePrice"]
            stock = one["reductionActivityInfo"]["remainStock"] if one["reductionActivityInfo"] else None
            img_url = one["picUrl"]
            meta = goods_id, goods_type_id, title, market_price, discount, sale_price, stock, img_url
            ggs.append((goods_id, goods_type_id))
            red(meta)
        return ggs

    def msg_to_queue(self, live_id: str):
        url = "https://i.meituan.com/mapi/dzu/live/livestudiobaseinfo.bin?"
        params = {
            "platform": "2",
            "appid": "10",
            "inapp": "false",
            "liveid": live_id,
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
                log.warning("直播间：{} | 无弹幕数据".format(live_id))
                return
        except:
            log.warning(resp.text)
            return

        begin_ts = jsdata["liveInfoVo"]["beginTime"]
        begin_tm = timef(begin_ts)
        _tip = "这是历史直播间，上次直播时间：{}".format(begin_tm) if begin_ts < time.time() * 1000 else ""

        for one in jsdata["messageVO"]["msgs"][::-1]:
            username = one["imUserDTO"]["userName"]
            uid = one["imUserDTO"]["userId"]
            content = one["imMsgDTO"]["content"]
            commentId = one["imMsgDTO"]["commentId"]
            unq_msg = "{} {} {} {}".format(username, uid, content, commentId)
            if unq_msg not in self.unq_msgs:
                self.unq_msgs.append(unq_msg)
                red("[聊天] {}（{}）：{}（{}）".format(username, uid, content, commentId))
                item = dict(type="ChatMessage", name=username, uid=uid, head_img="", content=content)
                self.msg_queue.put(item)
            else:
                log.debug(f"重复了 {unq_msg}")

    def listen(self, live_id=None, short_url=None):
        live_id = self.live_id if live_id is None and short_url is None else live_id or self.get_live_id(short_url)
        while True:
            self.msg_to_queue(live_id)
            time.sleep(random.randint(1, 3))

    def pull_msg(self):
        try:
            return self.msg_queue.get(timeout=10)
        except:
            pass

    def explain_goods(self, goods_id, goods_type_id):
        """弹商品卡"""
        url = "https://mlive.meituan.com/live/centercontrol/component/goods/goodssettopendpoint"
        params = {
            "liveid": self.live_id,
            "bizid": goods_id,
            "bizType": goods_type_id,
            "appid": "10",
            "yodaReady": "h5",
            "csecplatform": "4",
            "csecversion": "2.4.0"
        }
        res = session.get(url, headers=self.headers, params=params)
        red(res.text)

    def add_goods(self, goods_id, goods_type_id):
        """添加直播商品"""
        goods_id, goods_type_id = str(goods_id), str(goods_type_id)
        api = "https://mlive.meituan.com/live/centercontrol/component/goods/goodsbatchaddendpoint"
        params = {
            "appid": "10",
            "liveid": self.live_id,
            "yodaReady": "h5",
            "csecplatform": "4",
            "csecversion": "3.1.0"
        }
        data = {
            "liveid": self.live_id,
            "hidden": False,
            "goodsList": [
                {
                    "bizId": goods_id,
                    "bizType": goods_type_id,
                }
            ],
            "needResultExcel": False,
            "appid": 10
        }
        res = requests.post(api, params=params, headers=self.headers, json=data)
        red(res.text)

    def delete_goods(self, goods_id, goods_type_id):
        """删除直播商品"""
        url = "https://mlive.meituan.com/live/centercontrol/component/goods/goodsdeleteendpoint"
        params = {
            "bizid": goods_id,
            "biztype": goods_type_id,
            "hidden": "false",
            "liveid": self.live_id,
            "appid": "10",
            "yodaReady": "h5",
            "csecplatform": "4",
            "csecversion": "3.1.0"
        }
        res = requests.get(url, params, headers=self.headers)
        red(res.text)

    def sort_goods(self):
        """排序直播商品"""


def demo():
    live_id = 9496370
    short_url = "http://dpurl.cn/voNM8RIz"
    m = MeituanSpider()
    m.listen(live_id)


def demo2(live_id=None):
    m = MeituanSpider()
    t = threading.Thread(target=m.listen, args=(live_id,))
    t.daemon = True
    t.start()
    while True:
        item = m.pull_msg()
        if item:
            log.success(f"从队列取出  ==>  {item}")


def demo3(cookie: str):
    """随机弹一次商品卡"""
    m = MeituanSpider()
    m.ensure_cookie(cookie)
    ggs = m.crawl_goods()
    gg = random.choice(ggs)
    print("弹出", gg)
    m.explain_goods(*gg)


if __name__ == "__main__":
    # 2025/2/19 测试修改商品
    meituan = MeituanSpider()
    cookie = "uuid=90e82c208aae4c66b980.1731548694.1.0.0; _lxsdk_cuid=19328584150c8-0904ee868b3752-4c657b58-1fa400-19328584150c8; _ga=GA1.1.1078190637.1732238498; _ga_FSX5S86483=GS1.1.1732513784.2.0.1732513784.0.0.0; _ga_LYVVHCWVNG=GS1.1.1732513784.2.0.1732513784.0.0.0; iuuid=8CBE200AAAE11F3C9FC1305E8037CC1DBB492C39DEA4EAE4F593908FF2BEE706; _lxsdk=8CBE200AAAE11F3C9FC1305E8037CC1DBB492C39DEA4EAE4F593908FF2BEE706; lt=AgHbIEj86vnFq2i24xlwEclTj0n5IfQSpvYWRwQXytQA5yYEtbOBmRqy-MP5oRlo7iLcLv6brStarAAAAAAxJgAAPhLAzH0sKAz6ZjO8DD5pXeKxpz4WC4Yt7PyRTCROe-BZ_NIpGiGvqhM-21hQTlvf; u=3005615897; n=%E6%A9%99%E7%95%99%E9%A6%99aaa; mlive_anchor_token=2mliveanchorAgHbIEj86vnFq2i24xlwEclTj0n5IfQSpvYWRwQXytQA5yYEtbOBmRqy-MP5oRlo7iLcLv6brStarAAAAAAxJgAAPhLAzH0sKAz6ZjO8DD5pXeKxpz4WC4Yt7PyRTCROe-BZ_NIpGiGvqhM-21hQTlvf; __asource=pc; __UTYPE_2=2; edper=AgHbIEj86vnFq2i24xlwEclTj0n5IfQSpvYWRwQXytQA5yYEtbOBmRqy-MP5oRlo7iLcLv6brStarAAAAAAxJgAAPhLAzH0sKAz6ZjO8DD5pXeKxpz4WC4Yt7PyRTCROe-BZ_NIpGiGvqhM-21hQTlvf; token=AgHbIEj86vnFq2i24xlwEclTj0n5IfQSpvYWRwQXytQA5yYEtbOBmRqy-MP5oRlo7iLcLv6brStarAAAAAAxJgAAPhLAzH0sKAz6ZjO8DD5pXeKxpz4WC4Yt7PyRTCROe-BZ_NIpGiGvqhM-21hQTlvf; pragma-newtoken=AgHbIEj86vnFq2i24xlwEclTj0n5IfQSpvYWRwQXytQA5yYEtbOBmRqy-MP5oRlo7iLcLv6brStarAAAAAAxJgAAPhLAzH0sKAz6ZjO8DD5pXeKxpz4WC4Yt7PyRTCROe-BZ_NIpGiGvqhM-21hQTlvf; WEBDFPID=6w9zu3z2u8z35uwwz04745z319w8x4vx8067141vvu297958446wu7zu-1739927235146-1736302758502COKEQAYfd79fef3d01d5e9aadc18ccd4d0c95071380; _lxsdk_s=1951830902e-9f9-f02-81d%7C%7C29"
    meituan.ensure_cookie(cookie)
    meituan.live_id, gid, tid = 10038909, 1244770138, 9
    meituan.delete_goods(gid, tid)
    # meituan.add_goods(gid, tid)
    # meituan.explain_goods(gid, tid)
    # meituan.listen(meituan.live_id)
