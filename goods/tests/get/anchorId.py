import requests as req

from goods.configs import HEADERS

url = 'https://mlive.meituan.com/live/centercontrol/login/permissioncheck?liveid=&appid=10&yodaReady=h5&csecplatform=4&csecversion=2.4.0'
res = req.get(url, headers=HEADERS)
print(res.json())