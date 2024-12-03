import time

import requests as req
from fake_useragent import UserAgent
from loguru import logger


class BaseSpider():
    session = req.session()
    ua = UserAgent(platforms=["pc"], os=["windows"])

    def parse_url(self, url: str, retry=3, delay=1, ua: str = None) -> str:
        ua, headers = ua or self.ua.random, {"User-Agent": ua}
        _url = url[:100] + "..." if len(url) > 100 else url
        for i in range(retry + 1):
            try:
                logger.info("req ==> {}".format(_url))
                resp = self.session.get(url, headers=headers)
                return resp.text
            except Exception as e:
                logger.error(e)
                if i == retry:
                    raise Exception("达到最大重试了 => {}".format(_url))
                time.sleep(delay)
        return ""
