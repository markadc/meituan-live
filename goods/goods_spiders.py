import time

import requests as req
from fake_useragent import UserAgent
from loguru import logger

from goods.tests.parse import parse_goods

ua = UserAgent(platforms=["pc"], os=["windows"])


class GoodsSpider():
    def __init__(self, cookie: str):
        self.cookie = cookie
        self.headers = {"cookie": self.cookie, "User-Agent": ua.random}

    def crawl_goods(self, live_id: str):
        headers = {
            "Content-Type": "application/json",
            "startTime": str(time.time() * 1000),
            "Cookie": self.cookie,
            "User-Agent": ua.random,
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
        resp = req.post(url, headers=headers, params=params, json=data)
        print(live_id)
        parse_goods(resp.text)

    def crawl_anchor_id(self) -> str:
        url = 'https://mlive.meituan.com/live/centercontrol/login/permissioncheck?liveid=&appid=10&yodaReady=h5&csecplatform=4&csecversion=2.4.0'
        resp = req.get(url, headers=self.headers)
        anchor_id = resp.json()["data"]["anchorId"]
        return anchor_id

    def crawl_anchor_name(self, anchor_id: str) -> str:
        url = f"https://mlive.meituan.com/api/mlive/anchor/appanchorinfo.bin?anchorid={anchor_id}&usertype=2&appid=10&yodaReady=h5&csecplatform=4&csecversion=2.4.0"
        resp = req.get(url, headers=self.headers)
        anchor_name = resp.json()["data"]["anchorName"]
        return anchor_name

    def crawl_live_ids(self, anchor_id: str) -> list:
        params = {
            "playstatus": "1",
            "anchorid": anchor_id,
            "usertype": "2",
            "start": "0",
            "limit": "10",
            "appid": "10",
            "yodaReady": "h5",
            "csecplatform": "4",
            "csecversion": "2.4.0"
        }
        url = "https://mlive.meituan.com/api/mlive/anchor/apppagelives.bin"
        resp = req.get(url, params=params, headers=self.headers)
        data = resp.json()
        live_ids = [item["liveId"] for item in data["data"]]
        if len(live_ids) == 0:
            anchor_name = self.crawl_anchor_name(anchor_id)
            logger.warning("{}（{}） | 无直播计划".format(anchor_name, anchor_id))
        return live_ids


def test():
    cookie = "uuid=90e82c208aae4c66b980.1731548694.1.0.0; _lxsdk_cuid=19328584150c8-0904ee868b3752-4c657b58-1fa400-19328584150c8; WEBDFPID=6w9zu3z2u8z35uwwz04745z319w8x4vx8067141vvu297958446wu7zu-2046908734983-1731548734548SOMGSWMfd79fef3d01d5e9aadc18ccd4d0c95071170; wm_order_channel=default; swim_line=default; utm_source=; _ga=GA1.1.1078190637.1732238498; _ga_FSX5S86483=GS1.1.1732513784.2.0.1732513784.0.0.0; _ga_LYVVHCWVNG=GS1.1.1732513784.2.0.1732513784.0.0.0; __asource=pc; __UTYPE_3=3; iuuid=8CBE200AAAE11F3C9FC1305E8037CC1DBB492C39DEA4EAE4F593908FF2BEE706; mlive_anchor_token=2mliveanchorAgHRJdZGQPKCiFRob80TxEbJN6Ampae2heZzji65BIOecTz4HqlggFrtihVzfvZED1UmSeuI--S1aAAAAAAJJQAAVd1c1sCMz-eEDsFDpqy4qODg9w8wI1zzsQxkOgO6_ZpyvIh-Lsqil9Akv5LT-cZu; __UTYPE_2=2; edper=AgHRJdZGQPKCiFRob80TxEbJN6Ampae2heZzji65BIOecTz4HqlggFrtihVzfvZED1UmSeuI--S1aAAAAAAJJQAAVd1c1sCMz-eEDsFDpqy4qODg9w8wI1zzsQxkOgO6_ZpyvIh-Lsqil9Akv5LT-cZu; token=AgHRJdZGQPKCiFRob80TxEbJN6Ampae2heZzji65BIOecTz4HqlggFrtihVzfvZED1UmSeuI--S1aAAAAAAJJQAAVd1c1sCMz-eEDsFDpqy4qODg9w8wI1zzsQxkOgO6_ZpyvIh-Lsqil9Akv5LT-cZu; pragma-newtoken=AgHRJdZGQPKCiFRob80TxEbJN6Ampae2heZzji65BIOecTz4HqlggFrtihVzfvZED1UmSeuI--S1aAAAAAAJJQAAVd1c1sCMz-eEDsFDpqy4qODg9w8wI1zzsQxkOgO6_ZpyvIh-Lsqil9Akv5LT-cZu; _lxsdk=8CBE200AAAE11F3C9FC1305E8037CC1DBB492C39DEA4EAE4F593908FF2BEE706; _lx_utm=utm_source%3Dbing%26utm_medium%3Dorganic; _lxsdk_s=1939a8deef8-4d2-633-6d2%7C%7C154"
    spd = GoodsSpider(cookie)
    for live_id in spd.crawl_live_ids(spd.crawl_anchor_id()):
        spd.crawl_goods(live_id)


if __name__ == '__main__':
    test()
