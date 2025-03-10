import json
import time
from dataclasses import dataclass
from typing import Tuple, List

import requests
from loguru import logger as log
from rich.pretty import pprint


@dataclass
class Goods:
    name: str
    id: str
    type_id: str
    market_price: str
    discount: str
    sale_price: str
    stock: str
    cover: str

    def tozh(self):
        zh = {
            "商品名称": self.name,
            "商品ID": self.id,
            "原价": self.market_price,
            "折扣": self.discount,
            "现价": self.sale_price,
            "库存": self.stock,
            "封面图": self.cover
        }
        return zh


class MT_GoodsSpider:
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
        jsonData = json.loads(jsonStr)
        assert jsonData["code"] == 0, jsonStr

        print("{}（美团直播间ID）的商品信息如下".format(live_id))
        gtids = []
        for one in jsonData["data"]["goodsList"]:
            goods_id = one["goodsId"]
            goods_type_id = one["goodsType"]
            title = one["titleInfo"]["title"]
            market_price = one["goodsPriceInfo"]["marketPrice"]
            discount = one["goodsPriceInfo"]["discount"]
            sale_price = one["goodsPriceInfo"]["salePrice"]
            stock = one["reductionActivityInfo"]["remainStock"] if one["reductionActivityInfo"] else "不限"
            img_url = one["picUrl"]
            goods = Goods(name=title, id=goods_id, type_id=goods_type_id, market_price=market_price, discount=discount, sale_price=sale_price, stock=stock, cover=img_url)
            pprint(goods.tozh())
            gtids.append((goods_id, goods_type_id))
        return gtids

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

    def batch_add_goods(self, live_id, gtids: List[Tuple[int | str, int | str]]):
        """批量添加直播商品"""
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
            "goodsList": [{"bizId": v[0], "bizType": v[1]} for v in gtids],
            "needResultExcel": False,
            "appid": 10
        }
        log.debug("正在添加 {} 个商品".format(len(gtids)))
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
        log.debug("正在删除 1 个商品")
        res = requests.get(url, params, headers=self.headers)
        log.info(res.text)

    def batch_delete_goods(self, live_id, gtids: List[Tuple[str | int, str | int]]):
        """批量删除商品"""
        api = "https://mlive.meituan.com/live/centercontrol/component/goods/goodsbatchdeleteendpoint"
        params = {
            "appid": "10",
            "liveid": live_id,
            "yodaReady": "h5",
            "csecplatform": "4",
            "csecversion": "3.1.0"
        }
        data = {
            "liveid": live_id,
            "goodsList": [{"bizId": gtid[0], "bizType": gtid[1]} for gtid in gtids],
            "appid": 10
        }
        log.debug("正在删除 {} 个商品".format(len(gtids)))
        res = requests.post(api, params=params, headers=self.headers, json=data)
        log.info(res.text)

    def sort_goods(self, livd_id, gtids: list):
        """排序直播商品"""
        api = "https://mlive.meituan.com/live/centercontrol/component/goods/goodssortendpoint"
        params = {
            "appid": "10",
            "liveid": livd_id,
            "yodaReady": "h5",
            "csecplatform": "4",
            "csecversion": "3.1.0"
        }
        data = {
            "liveid": 10023596,
            "goodsList": [{"bizId": v[0], "bizType": v[1], "rank": i + 1, "rankChange": 1} for i, v in enumerate(gtids)],
            "isPagingSort": True,
            "appid": 10
        }
        log.debug("正在排序商品")
        res = requests.post(api, params=params, headers=self.headers, json=data)
        log.info(res.text)


if __name__ == '__main__':
    cookie = "uuid=90e82c208aae4c66b980.1731548694.1.0.0; _lxsdk_cuid=19328584150c8-0904ee868b3752-4c657b58-1fa400-19328584150c8; _ga=GA1.1.1078190637.1732238498; _ga_FSX5S86483=GS1.1.1732513784.2.0.1732513784.0.0.0; _ga_LYVVHCWVNG=GS1.1.1732513784.2.0.1732513784.0.0.0; iuuid=8CBE200AAAE11F3C9FC1305E8037CC1DBB492C39DEA4EAE4F593908FF2BEE706; _lxsdk=8CBE200AAAE11F3C9FC1305E8037CC1DBB492C39DEA4EAE4F593908FF2BEE706; lt=AgHbIEj86vnFq2i24xlwEclTj0n5IfQSpvYWRwQXytQA5yYEtbOBmRqy-MP5oRlo7iLcLv6brStarAAAAAAxJgAAPhLAzH0sKAz6ZjO8DD5pXeKxpz4WC4Yt7PyRTCROe-BZ_NIpGiGvqhM-21hQTlvf; u=3005615897; n=%E6%A9%99%E7%95%99%E9%A6%99aaa; mlive_anchor_token=2mliveanchorAgHbIEj86vnFq2i24xlwEclTj0n5IfQSpvYWRwQXytQA5yYEtbOBmRqy-MP5oRlo7iLcLv6brStarAAAAAAxJgAAPhLAzH0sKAz6ZjO8DD5pXeKxpz4WC4Yt7PyRTCROe-BZ_NIpGiGvqhM-21hQTlvf; __asource=pc; __UTYPE_2=2; edper=AgHbIEj86vnFq2i24xlwEclTj0n5IfQSpvYWRwQXytQA5yYEtbOBmRqy-MP5oRlo7iLcLv6brStarAAAAAAxJgAAPhLAzH0sKAz6ZjO8DD5pXeKxpz4WC4Yt7PyRTCROe-BZ_NIpGiGvqhM-21hQTlvf; token=AgHbIEj86vnFq2i24xlwEclTj0n5IfQSpvYWRwQXytQA5yYEtbOBmRqy-MP5oRlo7iLcLv6brStarAAAAAAxJgAAPhLAzH0sKAz6ZjO8DD5pXeKxpz4WC4Yt7PyRTCROe-BZ_NIpGiGvqhM-21hQTlvf; pragma-newtoken=AgHbIEj86vnFq2i24xlwEclTj0n5IfQSpvYWRwQXytQA5yYEtbOBmRqy-MP5oRlo7iLcLv6brStarAAAAAAxJgAAPhLAzH0sKAz6ZjO8DD5pXeKxpz4WC4Yt7PyRTCROe-BZ_NIpGiGvqhM-21hQTlvf; WEBDFPID=6w9zu3z2u8z35uwwz04745z319w8x4vx8067141vvu297958446wu7zu-1741655272925-1736302758502COKEQAYfd79fef3d01d5e9aadc18ccd4d0c95071380; _lxsdk_s=1957f72da12-b11-b6d-b3b%7C%7C47"
    meituan = MT_GoodsSpider(cookie)
    # lid = 10279311
    # gid = 1244770138
    # tid = 9
    # meituan.crawl_goods(10139816)
    # meituan.delete_goods(lid, gid, tid)
    # meituan.explain_goods(lid, gid, tid)

    # lid = 10045583
    # gtids = [(915819059, 9), (1127235825, 9), (1244770138, 9)]
    # meituan.batch_add_goods(lid, gtids)
    # meituan.batch_delete_goods(lid, gtids)
    # meituan.sort_goods(lid, gtids)
