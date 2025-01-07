from meituan import MeituanSpider

m = MeituanSpider()

# 方式1
short_url = "http://dpurl.cn/voNM8RIz"
m.listen(short_url=short_url)

# 方式2
live_id = "8742021"
m.listen(live_id=short_url)
