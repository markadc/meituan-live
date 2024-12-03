from live.http_way import MeituanListener
from goods import GoodsSpider

def test_listen():
    short_url = "http://dpurl.cn/voNM8RIz"
    liveid = "9050450"
    MeituanListener().listern_live(liveid)

def test_goods():
    cookie = 'uuid=90e82c208aae4c66b980.1731548694.1.0.0; _lxsdk_cuid=19328584150c8-0904ee868b3752-4c657b58-1fa400-19328584150c8; WEBDFPID=6w9zu3z2u8z35uwwz04745z319w8x4vx8067141vvu297958446wu7zu-2046908734983-1731548734548SOMGSWMfd79fef3d01d5e9aadc18ccd4d0c95071170; wm_order_channel=default; swim_line=default; utm_source=; _lxsdk=19328584150c8-0904ee868b3752-4c657b58-1fa400-19328584150c8; _ga=GA1.1.1078190637.1732238498; _ga_FSX5S86483=GS1.1.1732513784.2.0.1732513784.0.0.0; _ga_LYVVHCWVNG=GS1.1.1732513784.2.0.1732513784.0.0.0; _lx_utm=utm_source%3Dbing%26utm_medium%3Dorganic; __asource=pc; __UTYPE_3=3; iuuid=8CBE200AAAE11F3C9FC1305E8037CC1DBB492C39DEA4EAE4F593908FF2BEE706; lt=AgHRJdZGQPKCiFRob80TxEbJN6Ampae2heZzji65BIOecTz4HqlggFrtihVzfvZED1UmSeuI--S1aAAAAAAJJQAAVd1c1sCMz-eEDsFDpqy4qODg9w8wI1zzsQxkOgO6_ZpyvIh-Lsqil9Akv5LT-cZu; u=1843768220; n=Hjiah123; mlive_anchor_token=2mliveanchorAgHRJdZGQPKCiFRob80TxEbJN6Ampae2heZzji65BIOecTz4HqlggFrtihVzfvZED1UmSeuI--S1aAAAAAAJJQAAVd1c1sCMz-eEDsFDpqy4qODg9w8wI1zzsQxkOgO6_ZpyvIh-Lsqil9Akv5LT-cZu; __UTYPE_2=2; edper=AgHRJdZGQPKCiFRob80TxEbJN6Ampae2heZzji65BIOecTz4HqlggFrtihVzfvZED1UmSeuI--S1aAAAAAAJJQAAVd1c1sCMz-eEDsFDpqy4qODg9w8wI1zzsQxkOgO6_ZpyvIh-Lsqil9Akv5LT-cZu; token=AgHRJdZGQPKCiFRob80TxEbJN6Ampae2heZzji65BIOecTz4HqlggFrtihVzfvZED1UmSeuI--S1aAAAAAAJJQAAVd1c1sCMz-eEDsFDpqy4qODg9w8wI1zzsQxkOgO6_ZpyvIh-Lsqil9Akv5LT-cZu; pragma-newtoken=AgHRJdZGQPKCiFRob80TxEbJN6Ampae2heZzji65BIOecTz4HqlggFrtihVzfvZED1UmSeuI--S1aAAAAAAJJQAAVd1c1sCMz-eEDsFDpqy4qODg9w8wI1zzsQxkOgO6_ZpyvIh-Lsqil9Akv5LT-cZu; _lxsdk_s=1938a3e9770-07c-b74-bf4%7C%7C114'
    spd = GoodsSpider(cookie)
    for live_id in spd.crawl_live_ids(spd.crawl_anchor_id()):
        spd.crawl_goods(live_id)


if __name__ == "__main__":
    test_goods()
