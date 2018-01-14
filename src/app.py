import json
import sys
from models.TradeApi import TradeApi
from models.PublicApi import PublicApi
import time


class PmpBot:
    def __init__(self, pair):
        settings = json.load(open('../settings.json', 'r'))
        self.__tradeApiClient = TradeApi(settings["trade"]["key"], settings["trade"]["secret"],
                                         settings["urls"]["basicTrade"])
        self.__publicApiClient = PublicApi(settings["urls"]["basicPublic"])
        self.tradePair = pair
        self.initial_ask_rate = 0
        self.received = 0

    #  while have btc
    #  find sell order with the second small rate
    #  create buy order at such rate * (100/102) (as 2% - fee) for all btc in stock
    #  then if some amount of crypto to buy remains
    #  cancel the order and calculate btc in stock
    def run_buying(self):
        cur_ask_order = self.__publicApiClient.depth(self.tradePair)[self.tradePair.lower()]["asks"][1]
        self.initial_ask_rate = float(cur_ask_order[0])
        cur_ask_rate = self.initial_ask_rate

        cur_btc = float(self.__tradeApiClient.get_info()["return"]["funds"]["btc"])

        status = "fail"
        while cur_btc > 0 and cur_ask_rate < 3 * self.initial_ask_rate:
            make_order_res = self.__tradeApiClient.trade(self.tradePair, "buy",
                                                         cur_ask_rate, cur_btc * 100 / 102 / cur_ask_rate)

            success = True if make_order_res["success"] == 1 else False
            if success:
                received = float(make_order_res["return"]["received"])
                remains = float(make_order_res["return"]["remains"])
                order_id = int(make_order_res["return"]["order_id"])

                if remains == 0:
                    self.received += received
                    status = "success"
                    break
                else:
                    if received != 0:
                        status = "fine"
                        self.received += received
                        cur_btc = float(make_order_res["return"]["funds"]["btc"])
                        cur_btc += remains * cur_ask_rate * 102 / 100
                    self.__tradeApiClient.cancel_order(order_id)

            cur_ask_order = self.__publicApiClient.depth(self.tradePair)[self.tradePair.lower()]["asks"][1]
            cur_ask_rate = float(cur_ask_order[0])

        return status

    def run_selling(self):
        pass

    def work(self):
        buying_status = self.run_buying()
        if buying_status != "fail":
            self.run_selling()


if __name__ == '__main__':
    crypto = sys.argv[1]
    pmpBot = PmpBot(crypto + "_btc")
    pmpBot.work()
