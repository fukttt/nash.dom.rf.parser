import scrapy
import json


class BuildingsSpider(scrapy.Spider):
    name = "buildings"
    custom_settings = {
        "DUPEFILTER_CLASS": "scrapy.dupefilters.BaseDupeFilter",
    }
    start_urls = [
        "https://наш.дом.рф/%D1%81%D0%B5%D1%80%D0%B2%D0%B8%D1%81%D1%8B/%D0%BA%D0%B0%D1%82%D0%B0%D0%BB%D0%BE%D0%B3-%D0%BD%D0%BE%D0%B2%D0%BE%D1%81%D1%82%D1%80%D0%BE%D0%B5%D0%BA/%D1%81%D0%BF%D0%B8%D1%81%D0%BE%D0%BA-%D0%BE%D0%B1%D1%8A%D0%B5%D0%BA%D1%82%D0%BE%D0%B2/%D1%81%D0%BF%D0%B8%D1%81%D0%BE%D0%BA?place=0-6",
    ]
    ua = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
    offset = 0
    items = []
    parse_count = 512

    def start_requests(self):

        yield self.request(
            self.start_urls[0],
            self.parse,
        )

    def request(self, url, callback, meta={}):

        custom_headers = {
            "User-Agent": self.ua,
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Authorization": "Basic MTpxd2U=",
            "Connection": "keep-alive",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "Priority": "u=1",
            "Pragma": "no-cache",
            "Cache-Control": "no-cache",
            "TE": "trailers",
        }
        request = scrapy.Request(
            url=url, headers=custom_headers, callback=callback, meta=meta
        )
        return request

    def parse_another(self, response):
        responsejson = json.loads(response.text)
        item2 = response.meta["item"]
        item2["objTransferPlanDt"] = (
            responsejson["data"]["objTransferPlanDt"]
            if "objTransferPlanDt" in responsejson["data"]
            else "-"
        )
        item2["soldOutPerc"] = (
            responsejson["data"]["soldOutPerc"]
            if "soldOutPerc" in responsejson["data"]
            else "-"
        )

        yield {"data": item2, "offset": response.meta["offset"]}

    def parse(self, response):
        # https://xn--80az8a.xn--d1aqf.xn--p1ai/%D1%81%D0%B5%D1%80%D0%B2%D0%B8%D1%81%D1%8B/api/object/58791
        next_page = f"https://наш.дом.рф/%D1%81%D0%B5%D1%80%D0%B2%D0%B8%D1%81%D1%8B/api/kn/object?offset={self.offset}&limit=20&sortField=obj_publ_dt&sortType=desc&place=0-6"
        if "offset" in response.url:
            self.logger.debug(response.text)
            responsejson = json.loads(response.text)

            for i, el in enumerate(responsejson["data"]["list"]):
                item = {}

                item["local_id"] = i
                item["name"] = el["objCommercNm"] if "objCommercNm" in el else "-"
                item["objId"] = el["objId"] if "objId" in el else "-"
                item["exp_date"] = (
                    el["objReady100PercDt"] if "objReady100PercDt" in el else "-"
                )
                item["developer"] = (
                    el["developer"]["fullName"]
                    if "fullName" in el["developer"]
                    else "-"
                )
                item["developer_group"] = (
                    el["developer"]["groupName"]
                    if "groupName" in el["developer"]
                    else "-"
                )
                item["objPublDt"] = el["objPublDt"] if "objPublDt" in el else "-"
                item["objPriceAVG"] = el["objPriceAVG"] if "objPriceAVG" in el else "-"

                yield self.request(
                    "https://xn--80az8a.xn--d1aqf.xn--p1ai/%D1%81%D0%B5%D1%80%D0%B2%D0%B8%D1%81%D1%8B/api/object/"
                    + str(el["objId"]),
                    self.parse_another,
                    meta={"item": item, "offset": self.offset},
                )

            # if self.offset < 20:
            #     self.offset += 20
            if self.offset < self.parse_count:
                self.offset += 20
                yield self.request(next_page, self.parse)
        else:
            yield self.request(next_page, self.parse)
