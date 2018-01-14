import requests
import urllib.parse


class PublicApi:
    def __init__(self, basic_url):
        self.__basicUrl = basic_url

    def query_api(self, method, pair=None, params=None):
        query_url = self.__basicUrl + method

        if pair:
            query_url += "/{}".format(pair.lower())
            if params:
                params_url_string = urllib.parse.urlencode(params)
                query_url += "?{}".format(params_url_string)

        return requests.get(query_url).json()

    def info(self):
        return self.query_api("info")

    def depth(self, pair, limit=5):
        return self.query_api("depth", pair, {"limit": limit})
