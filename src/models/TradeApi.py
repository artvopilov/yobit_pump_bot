import hmac
import hashlib
import time
import urllib.parse
import requests


class TradeApi:
    def __init__(self, key, secret, basic_url):
        self.__key = key
        self.__secret = secret
        self.__basicUrl = basic_url

    def make_signature(self, params):
        sign = hmac.new(self.__secret.encode(), params.encode(), hashlib.sha512)  # hmac - hash-based ... code
        return sign.hexdigest()  # Получение зашифрованной строки

    def query_api(self, method, params=None):
        if not params:
            params = {}

        params["method"] = method
        params["nonce"] = int(time.time())
        params_url_string = urllib.parse.urlencode(params)  # Преобазование json в url строку

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Key': self.__key,
            'Sign': self.make_signature(params_url_string)
        }

        return requests.post(self.__basicUrl, data=params, headers=headers).json()

    def get_info(self):
        return self.query_api("getInfo")

    def trade(self, pair, type_tr, rate, amount):
        return self.query_api("Trade", {"pair": pair, "type": type_tr, "rate": rate, "amount": amount})

    def cancel_order(self, order_id):
        return self.query_api("CancelOrder", {"order_id": order_id})
