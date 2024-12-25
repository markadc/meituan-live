import threading
import time
from functools import partial
from queue import Queue

import requests
from wauo.utils import Loger, cprint

print = partial(cprint, color="red")

loger = Loger()

ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0"
default_headers = {"upgrade-insecure-requests": "1", "user-agent": ua}

session = requests.Session()
session.headers.update(default_headers)


class MeituanSpider:
    msg_queue = Queue()
    unq_msgs = []

    def close_live(self, cookie, live_id):
        url = f"https://mlive.meituan.com/live/centercontrol/component/liveadmin/stoplive?liveid={live_id}&appid=10&yodaReady=h5&csecplatform=4&csecversion=2.4.0"
        headers = {"User-Agent": ua, "Cookie": cookie}
        res = requests.get(url, headers=headers)
        print(res.text)

    def start_live(self, cookie, live_id):
        url = f"https://mlive.meituan.com/live/centercontrol/component/liveadmin/startlive?liveid={live_id}&appid=10&yodaReady=h5&csecplatform=4&csecversion=2.4.0"
        headers = {"User-Agent": ua, "Cookie": cookie}
        res = requests.get(url, headers=headers)
        print(res.text)

    def get_liveid(self, short_url: str) -> str:
        resp = session.get(short_url, allow_redirects=False)
        new_url = resp.headers["Location"]
        loger.info("{} => {}".format(resp.status_code, new_url))
        liveid = new_url.split("liveid=")[1].split("&")[0]
        loger.info("已获取到liveid为{}".format(liveid))
        return liveid

    def msg_to_queue(self, liveid: str):
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
                loger.warning("直播间：{} | 无弹幕数据".format(liveid))
                return
        except:
            loger.warning(resp.text)
            return

        for one in jsdata["messageVO"]["msgs"][::-1]:
            username = one["imUserDTO"]["userName"]
            uid = one["imUserDTO"]["userId"]
            content = one["imMsgDTO"]["content"]
            commentId = one["imMsgDTO"]["commentId"]
            unq_msg = "{} {} {} {}".format(username, uid, content, commentId)
            item = dict(
                type="ChatMessage",
                name=username,
                uid=uid,
                head_img="",
                content=content,
            )
            if unq_msg not in self.unq_msgs:
                self.unq_msgs.append(unq_msg)
                print("[聊天] {}（{}）：{}".format(username, uid, content))
                self.msg_queue.put(item)
            else:
                loger.debug(f"重复了 {unq_msg}")

    def listen(self, liveid: str = None, short_url: str = None):
        assert liveid or short_url, "无目标源"
        liveid = liveid or self.get_liveid(short_url)
        while True:
            self.msg_to_queue(liveid)
            time.sleep(2)

    def pull_msg(self):
        try:
            return self.msg_queue.get(timeout=10)
        except:
            pass

    def explain_goods(self, cookie, live_id, goods_id, goods_type_id):
        headers = {"User-Agent": ua, "Cookie": cookie}
        url = "https://mlive.meituan.com/live/centercontrol/component/goods/goodssettopendpoint"
        params = {
            "liveid": live_id,
            "bizid": goods_id,
            "bizType": goods_type_id,
            "appid": "10",
            "yodaReady": "h5",
            "csecplatform": "4",
            "csecversion": "2.4.0"
        }
        response = session.get(url, headers=headers, params=params)
        print(response.text)


def test():
    short_url = "http://dpurl.cn/voNM8RIz"
    liveid = "9393594"
    MeituanSpider().listen(liveid)


def test2():
    liveid = "9393594"
    m = MeituanSpider()
    t1 = threading.Thread(target=m.listen, args=(liveid,))
    t1.start()

    while True:
        item = m.pull_msg()
        if item:
            loger.success(f"从队列取出  ==>  {item}")


def test3():
    """测试，弹商品卡"""
    cookie = "uuid=90e82c208aae4c66b980.1731548694.1.0.0; _lxsdk_cuid=19328584150c8-0904ee868b3752-4c657b58-1fa400-19328584150c8; WEBDFPID=6w9zu3z2u8z35uwwz04745z319w8x4vx8067141vvu297958446wu7zu-2046908734983-1731548734548SOMGSWMfd79fef3d01d5e9aadc18ccd4d0c95071170; _ga=GA1.1.1078190637.1732238498; _ga_FSX5S86483=GS1.1.1732513784.2.0.1732513784.0.0.0; _ga_LYVVHCWVNG=GS1.1.1732513784.2.0.1732513784.0.0.0; iuuid=8CBE200AAAE11F3C9FC1305E8037CC1DBB492C39DEA4EAE4F593908FF2BEE706; _lxsdk=8CBE200AAAE11F3C9FC1305E8037CC1DBB492C39DEA4EAE4F593908FF2BEE706; __asource=pc; __UTYPE_3=3; __UTYPE_2=2; _lx_utm=utm_source%3Dbing%26utm_medium%3Dorganic; mtcdn=K; lt=AgFjIIzaiKoyBCEG7-iZ_uFLnM76roF_MKYO_3B7u9OE5jy9f8Pg4G0p9yX2Zr9fLettL1PAEGxbzQAAAABrJQAAGQeCD3n3x6juH1svRl_GcbR_xqvSDRERi2Uve14Dab98S4471YqbFvyyP1c8AdO8; u=3005615897; n=%E6%A9%99%E7%95%99%E9%A6%99aaa; mlive_anchor_token=2mliveanchorAgFjIIzaiKoyBCEG7-iZ_uFLnM76roF_MKYO_3B7u9OE5jy9f8Pg4G0p9yX2Zr9fLettL1PAEGxbzQAAAABrJQAAGQeCD3n3x6juH1svRl_GcbR_xqvSDRERi2Uve14Dab98S4471YqbFvyyP1c8AdO8; edper=AgFjIIzaiKoyBCEG7-iZ_uFLnM76roF_MKYO_3B7u9OE5jy9f8Pg4G0p9yX2Zr9fLettL1PAEGxbzQAAAABrJQAAGQeCD3n3x6juH1svRl_GcbR_xqvSDRERi2Uve14Dab98S4471YqbFvyyP1c8AdO8; token=AgFjIIzaiKoyBCEG7-iZ_uFLnM76roF_MKYO_3B7u9OE5jy9f8Pg4G0p9yX2Zr9fLettL1PAEGxbzQAAAABrJQAAGQeCD3n3x6juH1svRl_GcbR_xqvSDRERi2Uve14Dab98S4471YqbFvyyP1c8AdO8; pragma-newtoken=AgFjIIzaiKoyBCEG7-iZ_uFLnM76roF_MKYO_3B7u9OE5jy9f8Pg4G0p9yX2Zr9fLettL1PAEGxbzQAAAABrJQAAGQeCD3n3x6juH1svRl_GcbR_xqvSDRERi2Uve14Dab98S4471YqbFvyyP1c8AdO8; _lxsdk_s=193fc982674-603-2ac-83d%7C%7C52"
    live_id = "9423883"
    # goods_id = "885732936"  # 80 代 100 元代金券
    # goods_id = "970184788"  # 60分钟足疗
    # goods_id = "1192575776"  # 【疲劳解压】｜60分钟全身精油SPA
    goods_id = "1171387952"  # 【解压放松】精油开背｜刮痧
    m = MeituanSpider()
    # m.explain_goods(cookie, live_id, goods_id, 9)
    m.explain_goods(cookie, live_id, "1209348083", 9)


if __name__ == "__main__":
    # test()
    # test2()
    # test3()
    cookie = "uuid=90e82c208aae4c66b980.1731548694.1.0.0; _lxsdk_cuid=19328584150c8-0904ee868b3752-4c657b58-1fa400-19328584150c8; WEBDFPID=6w9zu3z2u8z35uwwz04745z319w8x4vx8067141vvu297958446wu7zu-2046908734983-1731548734548SOMGSWMfd79fef3d01d5e9aadc18ccd4d0c95071170; _ga=GA1.1.1078190637.1732238498; _ga_FSX5S86483=GS1.1.1732513784.2.0.1732513784.0.0.0; _ga_LYVVHCWVNG=GS1.1.1732513784.2.0.1732513784.0.0.0; iuuid=8CBE200AAAE11F3C9FC1305E8037CC1DBB492C39DEA4EAE4F593908FF2BEE706; _lxsdk=8CBE200AAAE11F3C9FC1305E8037CC1DBB492C39DEA4EAE4F593908FF2BEE706; __asource=pc; __UTYPE_3=3; __UTYPE_2=2; mtcdn=K; lt=AgFjIIzaiKoyBCEG7-iZ_uFLnM76roF_MKYO_3B7u9OE5jy9f8Pg4G0p9yX2Zr9fLettL1PAEGxbzQAAAABrJQAAGQeCD3n3x6juH1svRl_GcbR_xqvSDRERi2Uve14Dab98S4471YqbFvyyP1c8AdO8; u=3005615897; n=%E6%A9%99%E7%95%99%E9%A6%99aaa; mlive_anchor_token=2mliveanchorAgFjIIzaiKoyBCEG7-iZ_uFLnM76roF_MKYO_3B7u9OE5jy9f8Pg4G0p9yX2Zr9fLettL1PAEGxbzQAAAABrJQAAGQeCD3n3x6juH1svRl_GcbR_xqvSDRERi2Uve14Dab98S4471YqbFvyyP1c8AdO8; edper=AgFjIIzaiKoyBCEG7-iZ_uFLnM76roF_MKYO_3B7u9OE5jy9f8Pg4G0p9yX2Zr9fLettL1PAEGxbzQAAAABrJQAAGQeCD3n3x6juH1svRl_GcbR_xqvSDRERi2Uve14Dab98S4471YqbFvyyP1c8AdO8; token=AgFjIIzaiKoyBCEG7-iZ_uFLnM76roF_MKYO_3B7u9OE5jy9f8Pg4G0p9yX2Zr9fLettL1PAEGxbzQAAAABrJQAAGQeCD3n3x6juH1svRl_GcbR_xqvSDRERi2Uve14Dab98S4471YqbFvyyP1c8AdO8; pragma-newtoken=AgFjIIzaiKoyBCEG7-iZ_uFLnM76roF_MKYO_3B7u9OE5jy9f8Pg4G0p9yX2Zr9fLettL1PAEGxbzQAAAABrJQAAGQeCD3n3x6juH1svRl_GcbR_xqvSDRERi2Uve14Dab98S4471YqbFvyyP1c8AdO8; _lx_utm=utm_source%3Dbing%26utm_medium%3Dorganic; _lxsdk_s=193fce62be1-3a9-f6e-8ab%7C%7C86"
    live_id = "9426028"
    MeituanSpider().start_live(cookie, live_id)
