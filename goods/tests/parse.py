import json


def parse_goods(json_str: str):
    data = json.loads(json_str)
    assert data["code"] == 0, json_str
    for one in data["data"]["goodsList"]:
        goods_id = one["goodsId"]
        title = one["titleInfo"]["title"]
        market_price = one["goodsPriceInfo"]["marketPrice"]
        discount = one["goodsPriceInfo"]["discount"]
        sale_price = one["goodsPriceInfo"]["salePrice"]
        stock = one["reductionActivityInfo"]["remainStock"] if one["reductionActivityInfo"] else None
        img_url = one["picUrl"]
        meta = goods_id, title, market_price, discount, sale_price, stock, img_url
        print(meta)
