import json
import time

import requests
from loguru import logger as log


class MeituanGoodsSpider:
    def __init__(self, cookie: str):
        self.cookie = cookie
        self.ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0"
        self.headers = {"Cookie": self.cookie, "User-Agent": self.ua}

    def crawl_goods(self, live_id):
        """抓取当前直播商品"""
        headers = {
            "Content-Type": "application/json",
            "startTime": str(time.time() * 1000),
            "Cookie": self.cookie,
            "User-Agent": self.ua,
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
        resp = requests.post(url, headers=headers, params=params, json=data)
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
            print(meta)
        return ggs

    def explain_goods(self, live_id, goods_id, goods_type_id):
        """弹商品卡"""
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
        res = requests.get(url, params, headers=self.headers)
        log.info(res.text)

    def add_goods(self, live_id, goods_id, goods_type_id):
        """添加直播商品"""
        goods_id, goods_type_id = str(goods_id), str(goods_type_id)
        api = "https://mlive.meituan.com/live/centercontrol/component/goods/goodsbatchaddendpoint"
        params = {
            "appid": "10",
            "liveid": live_id,
            "yodaReady": "h5",
            "csecplatform": "4",
            "csecversion": "3.1.0"
        }
        data = {
            "liveid": live_id,
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
        log.info(res.text)

    def delete_goods(self, live_id, goods_id, goods_type_id):
        """删除直播商品"""
        url = "https://mlive.meituan.com/live/centercontrol/component/goods/goodsdeleteendpoint"
        params = {
            "bizid": goods_id,
            "biztype": goods_type_id,
            "hidden": "false",
            "liveid": live_id,
            "appid": "10",
            "yodaReady": "h5",
            "csecplatform": "4",
            "csecversion": "3.1.0"
        }
        res = requests.get(url, params, headers=self.headers)
        log.info(res.text)

    def sort_goods(self):
        """排序直播商品"""


if __name__ == '__main__':
    cookie = "uuid=90e82c208aae4c66b980.1731548694.1.0.0; _lxsdk_cuid=19328584150c8-0904ee868b3752-4c657b58-1fa400-19328584150c8; _ga=GA1.1.1078190637.1732238498; _ga_FSX5S86483=GS1.1.1732513784.2.0.1732513784.0.0.0; _ga_LYVVHCWVNG=GS1.1.1732513784.2.0.1732513784.0.0.0; iuuid=8CBE200AAAE11F3C9FC1305E8037CC1DBB492C39DEA4EAE4F593908FF2BEE706; _lxsdk=8CBE200AAAE11F3C9FC1305E8037CC1DBB492C39DEA4EAE4F593908FF2BEE706; lt=AgHbIEj86vnFq2i24xlwEclTj0n5IfQSpvYWRwQXytQA5yYEtbOBmRqy-MP5oRlo7iLcLv6brStarAAAAAAxJgAAPhLAzH0sKAz6ZjO8DD5pXeKxpz4WC4Yt7PyRTCROe-BZ_NIpGiGvqhM-21hQTlvf; u=3005615897; n=%E6%A9%99%E7%95%99%E9%A6%99aaa; mlive_anchor_token=2mliveanchorAgHbIEj86vnFq2i24xlwEclTj0n5IfQSpvYWRwQXytQA5yYEtbOBmRqy-MP5oRlo7iLcLv6brStarAAAAAAxJgAAPhLAzH0sKAz6ZjO8DD5pXeKxpz4WC4Yt7PyRTCROe-BZ_NIpGiGvqhM-21hQTlvf; __asource=pc; __UTYPE_2=2; edper=AgHbIEj86vnFq2i24xlwEclTj0n5IfQSpvYWRwQXytQA5yYEtbOBmRqy-MP5oRlo7iLcLv6brStarAAAAAAxJgAAPhLAzH0sKAz6ZjO8DD5pXeKxpz4WC4Yt7PyRTCROe-BZ_NIpGiGvqhM-21hQTlvf; token=AgHbIEj86vnFq2i24xlwEclTj0n5IfQSpvYWRwQXytQA5yYEtbOBmRqy-MP5oRlo7iLcLv6brStarAAAAAAxJgAAPhLAzH0sKAz6ZjO8DD5pXeKxpz4WC4Yt7PyRTCROe-BZ_NIpGiGvqhM-21hQTlvf; pragma-newtoken=AgHbIEj86vnFq2i24xlwEclTj0n5IfQSpvYWRwQXytQA5yYEtbOBmRqy-MP5oRlo7iLcLv6brStarAAAAAAxJgAAPhLAzH0sKAz6ZjO8DD5pXeKxpz4WC4Yt7PyRTCROe-BZ_NIpGiGvqhM-21hQTlvf; WEBDFPID=6w9zu3z2u8z35uwwz04745z319w8x4vx8067141vvu297958446wu7zu-1739927235146-1736302758502COKEQAYfd79fef3d01d5e9aadc18ccd4d0c95071380; _lxsdk_s=1951830902e-9f9-f02-81d%7C%7C29"
    meituan = MeituanGoodsSpider(cookie)
    lid = 10039738
    gid = 1244770138
    tid = 9
    meituan.crawl_goods(lid)
    # meituan.add_goods(lid, gid, tid)
    # meituan.delete_goods(lid, gid, tid)
    # meituan.explain_goods(lid, gid, tid)
