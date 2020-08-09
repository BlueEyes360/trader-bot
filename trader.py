"""
    TraderBot - TODO: abstract out later to config file instantiation
    Source: https://blog.usejournal.com/a-step-by-step-guide-to-building-a-trading-bot-in-any-programming-language-d202ffe91569
    Exchange: Coinbase
    From: USD
    To: BTC
"""


from time import sleep
from random import random
import cbpro
import json

from secrets import Viewer_CoinBase_Secret, Viewer_CoinBase_Key, Passphrase, Sandbox_URL, Sandbox_Secret, Sandbox_Key, Sandbox_Passphrase, Sandbox_USD_GUID, Sandbox_BTC_GUID

class TraderBot:

    def __init__(self):
        self.isNextOperationBuy = True

        self.UPWARD_TREND_THRESHOLD = 1.5
        self.DIP_THRESHOLD = -2.25

        self.PROFIT_THRESHOLD = 1.25
        self.STOP_LOSS_THRESHOLD = -2.0

        self.BALANCE = 100.0

        # self.client = cbpro.PublicClient()
        self.client = cbpro.AuthenticatedClient(Sandbox_Key, Sandbox_Secret, Sandbox_Passphrase, api_url=Sandbox_URL)
        _initResponse = self.client.get_product_ticker(product_id='BTC-USD')
        self.lastOpPrice = float(_initResponse["price"])

    def __str__(self):
        """ Used natively by Python to print out TraderBot representation """
        result = "TraderBot:\n"
        return result


    def __repr__(self):
        """ Used natively by Python to print out TraderBot usage  """
        return "TraderBot()".format()

    def getBalance(self):
        """ Get amount of USD currently in account """
        print("getBalances()")
        response = self.client.get_account(Sandbox_USD_GUID)

        return(float(response["balance"]))


    def getMarketPrice(self):
        """ Get the current market price of BTC in comparison to USD """
        response = self.client.get_product_ticker(product_id='BTC-USD')
        price = float(response["price"])

        return price


    def placeSellOrder(self):
        """ """
        amount = self.calculateSellAmount()
        print("placeSellOrder() - {}".format(amount))
        response = self.client.place_market_order(product_id='BTC-USD', side='sell', funds=amount)


    def placeBuyOrder(self):
        """ """
        amount = self.calculateBuyAmount()
        print("placeBuyOrder() - {}".format(amount))
        response = self.client.place_market_order(product_id='BTC-USD', side='buy', funds=amount)

        return response


    def getOperationDetails(self):
        ''' Optional '''
        print("getOperationDetails()")


    def startBot(self):
        """ """
        try:
            while True:
                # print("attemptToMakeTrade()")
                self.attemptToMakeTrade()
                sleep(30)
        except KeyboardInterrupt as exc:
            print("Exiting...")


    def tryToBuy(self, percentDiff):
        """ """
        if percentDiff >= self.UPWARD_TREND_THRESHOLD or percentDiff <= self.DIP_THRESHOLD:
            # self.lastOpPrice = self.placeBuyOrder()
            previousOpPrice = self.lastOpPrice
            self.lastOpPrice = self.getMarketPrice()
            self.isNextOperationBuy = False
            print("tryToBuy() successful!\nnewLastOp:\t{}%\nprevLastOp:\t{}\n\t".format(percentDiff, self.lastOpPrice, previousOpPrice))


    def tryToSell(self, percentDiff):
        """ """
        if percentDiff >= self.PROFIT_THRESHOLD or percentDiff <= self.STOP_LOSS_THRESHOLD:
            # self.lastOpPrice = self.placeSellOrder()
            previousOpPrice = self.lastOpPrice
            self.lastOpPrice = self.getMarketPrice()
            self.isNextOperationBuy = True
            print("tryToSell() successful!\nnewLastOp:\t{}%\nprevLastOp:\t{}\n\t".format(percentDiff, self.lastOpPrice, previousOpPrice))


    def attemptToMakeTrade(self):
        """ """
        currentPrice = self.getMarketPrice()
        percentageDiff = (currentPrice - self.lastOpPrice) / self.lastOpPrice * 100
        if self.isNextOperationBuy:
            self.tryToBuy(percentageDiff)
        else:
            self.tryToSell(percentageDiff)


    def calculateBuyAmount(self):
        """
            Used to calculate how much to buy based on current balance of USD

            Currently buys are bound by:
                $20 as a minimal balance to buy anything, less and no buys will happen (return 0)
                $100 as maximal purchase

            These bounds are subject to removal or change
        """
        balance = self.getBalance()
        amount = 100
        if ((balance / 2) < 100):
            amount = balance / 2

        if balance < 20:
            return 0

        return amount


    def calculateSellAmount(self):
        """
            Used to calculate how much to sell based on current balance of BTC

            Currently sells are for the entirety of the amount of BTC currently owned
        """
        response = self.client.get_account(Sandbox_BTC_GUID)
        amount = response["balance"]

        return amount


def pp(obj):
    """ Pretty print utility function """
    print(json.dumps(obj, indent=4))


if __name__ == "__main__":
    tb = TraderBot()
    # balance = tb.getBalance()
    res = tb.placeBuyOrder()

    pp(res)
    # print("Initial price:\t{}\n".format(tb.lastOpPrice))
    # tb.startBot()
    # price = tb.getMarketPrice()
    # print(price)
    # public_client = cbpro.PublicClient()
    # products = public_client.get_products()
    # eth_usd = public_client.get_product_ticker(product_id='ETH-USD')
    # eth_hist = public_client.get_product_historic_rates('ETH-USD')

    # auth_client = cbpro.AuthenticatedClient(Viewer_CoinBase_Key, Viewer_CoinBase_Secret, Passphrase)
    # eth_usd = auth_client.get_product_ticker(product_id='ETH-USD')
    # accounts = auth_client.get_accounts()

    # sand_auth_client = cbpro.AuthenticatedClient(Sandbox_Key, Sandbox_Secret, Sandbox_Passphrase, api_url=Sandbox_URL)
    # eth_usd = sand_auth_client.get_product_ticker(product_id='ETH-USD')
    # accounts = sand_auth_client.get_accounts()


    # for product in products:
    #     print(json.dumps(product, indent=4))

    # pp(eth_usd)
    # pp(accounts)
    # pp(eth_hist)