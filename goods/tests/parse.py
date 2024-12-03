import json


def parse_goods(json_str: str):
    data = json.loads(json_str)
    assert data["code"] == 0, json_str
    all_goods = data["data"]["goodsList"]
    for goods in all_goods:
        title = goods["titleInfo"]["title"]
        market_price = goods["goodsPriceInfo"]["marketPrice"]
        discount = goods["goodsPriceInfo"]["discount"]
        sale_price = goods["goodsPriceInfo"]["salePrice"]
        img_url = goods["picUrl"]
        some = title, market_price, discount, sale_price, img_url
        print(some)
