import requests

from goods.configs import COOKIE

headers = {
    "Cookie": COOKIE,
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0",
}
params = {
    "playstatus": "1",
    "anchorid": "431516",
    "usertype": "2",
    "start": "0",
    "limit": "10",
    "appid": "10",
    "yodaReady": "h5",
    "csecplatform": "4",
    "csecversion": "2.4.0"
}
url = "https://mlive.meituan.com/api/mlive/anchor/apppagelives.bin"
response = requests.get(url, headers=headers, params=params)
data = response.json()
for item in data["data"]:
    print(item)
