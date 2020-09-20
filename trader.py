"""
    TraderBot - TODO: abstract out later to config file instantiation
    Source: https://blog.usejournal.com/a-step-by-step-guide-to-building-a-trading-bot-in-any-programming-language-d202ffe91569
    Exchange: Coinbase
    From: USD
    To: BTC
    cbpro from https://github.com/danpaquin/coinbasepro-python
"""


from time import sleep
import datetime
from random import random
import cbpro
import json

from secrets import Viewer_CoinBase_Secret, Viewer_CoinBase_Key, Passphrase, Sandbox_URL, Sandbox_Secret, Sandbox_Key, Sandbox_Passphrase, Sandbox_USD_GUID, Sandbox_BTC_GUID
from secrets import Buyer_CoinBase_Secret, Buyer_CoinBase_Key, Buyer_Passphrase, Buyer_USD_GUID, Buyer_BTC_GUID

class TraderBot:

    def __init__(self):
        self.isNextOperationBuy = True


        self.UPWARD_TREND_THRESHOLD = 1.0
        self.DIP_THRESHOLD = -1.0
        self.PROFIT_THRESHOLD = 1.5
        self.STOP_LOSS_THRESHOLD = -2.0

        # self.UPWARD_TREND_THRESHOLD = 1.5
        # self.DIP_THRESHOLD = -1.75
        # self.PROFIT_THRESHOLD = 1.35
        # self.STOP_LOSS_THRESHOLD = -2.0

        # self.UPWARD_TREND_THRESHOLD = 3.0
        # self.DIP_THRESHOLD = -4.5
        # self.PROFIT_THRESHOLD = 2.5
        # self.STOP_LOSS_THRESHOLD = -4.0

        # self.UPWARD_TREND_THRESHOLD = 0.75
        # self.DIP_THRESHOLD = -1.125
        # self.PROFIT_THRESHOLD = 0.625
        # self.STOP_LOSS_THRESHOLD = -1.0

        # Any change, do something for testing
        # self.UPWARD_TREND_THRESHOLD = 0.0075
        # self.DIP_THRESHOLD = -0.0125
        # self.PROFIT_THRESHOLD = 0.0125
        # self.STOP_LOSS_THRESHOLD = -0.05


        self.BALANCE = 100.0

        self.client = cbpro.AuthenticatedClient(Buyer_CoinBase_Key, Buyer_CoinBase_Secret, Buyer_Passphrase)

        # self.client = cbpro.AuthenticatedClient(Sandbox_Key, Sandbox_Secret, Sandbox_Passphrase, api_url=Sandbox_URL)
        # self.client = cbpro.AuthenticatedClient(Viewer_CoinBase_Key, Viewer_CoinBase_Secret, Passphrase)
        self.lastOpPrice = self.getMarketPrice()

    def __str__(self):
        """ Used natively by Python to print out TraderBot representation """
        result = "TraderBot:\n"
        return result


    def __repr__(self):
        """ Used natively by Python to print out TraderBot usage  """
        return "TraderBot()".format()

    def getBalance(self):
        """ Get amount of USD currently in account """
        # print("getBalances()")
        response = self.client.get_account(Buyer_USD_GUID)

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

        return response


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
        print("Beginning TraderBot:\n\tInitial price: {}".format(self.lastOpPrice))
        counter = 0
        try:
            while True:
                # print("attemptToMakeTrade()")
                print(".", end='', flush=True)

                if counter % 20 == 0:
                    currentPrice = self.getMarketPrice()
                    percentageDiff = ( currentPrice - self.lastOpPrice) / self.lastOpPrice * 100
                    print("\nTime: {}\tCurr: {}\tLast: {}\t{}% diff".format(datetime.datetime.now(), currentPrice, self.lastOpPrice, percentageDiff))
                counter += 1

                self.attemptToMakeTrade()
                sleep(30)

        except KeyboardInterrupt as exc:
            print("Exiting...")


    def tryToBuy(self, percentDiff):
        """ """
        if percentDiff >= self.UPWARD_TREND_THRESHOLD or percentDiff <= self.DIP_THRESHOLD:
            previousOpPrice = self.lastOpPrice
            response = self.placeBuyOrder()
            pp(response)
            # orderNum = response["id"]
            # while response["status"] is "pending":
            #     response = self.client.get_order(orderNum)
            #     if response["status"] is not "pending":

            self.lastOpPrice = self.getMarketPrice()
            self.isNextOperationBuy = False
            print("\ntryToBuy() successful!\n{} %\nnewLastOp:\t{}\nprevLastOp:\t{}\n\t".format(percentDiff, self.lastOpPrice, previousOpPrice))


    def tryToSell(self, percentDiff):
        """ """
        if percentDiff >= self.PROFIT_THRESHOLD or percentDiff <= self.STOP_LOSS_THRESHOLD:
            previousOpPrice = self.lastOpPrice
            response = self.placeSellOrder()
            pp(response)
            # orderNum = response["id"]

            self.lastOpPrice = self.getMarketPrice()
            self.isNextOperationBuy = True
            print("\ntryToSell() successful!\n{} %\nnewLastOp:\t{}\nprevLastOp:\t{}\n\t".format(percentDiff, self.lastOpPrice, previousOpPrice))


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

        return float("{:.2f}".format(amount))


    def calculateSellAmount(self):
        """
            Used to calculate how much to sell based on current balance of BTC

            Currently sells are for the entirety of the amount of BTC currently owned
        """
        response = self.client.get_account(Buyer_BTC_GUID)
        amount = float(response["balance"]) * self.getMarketPrice()

        return float("{:.2f}".format(amount))


def pp(obj):
    """ Pretty print utility function """
    print(json.dumps(obj, indent=4))


if __name__ == "__main__":
    tb = TraderBot()
    tb.startBot()
    # tb.tryToBuy(1.7)
    # balance = tb.getBalance()
    # res = tb.placeBuyOrder()
    # res = tb.placeSellOrder()
    # pp(res)

    # response = tb.client.place_market_order(product_id='BTC-USD', side='buy', funds=50.0)
    # print("Buy:")
    # pp(response)

    # response = tb.client.place_market_order(product_id='BTC-USD', side='sell', funds=50.0)
    # print("Sell:")
    # pp(response)

    # depositParams = {
    #     'amount': '100.00', # Currency determined by account specified
    #     'coinbase_account_id': '1JmYrFBLMSCLBwoL87gdQ5Qc9MLvb2egKk',
    #     'currency': 'BTC',
    #     'payment_method_id': '1JmYrFBLMSCLBwoL87gdQ5Qc9MLvb2egKk'
    # }

    # res = tb.client.deposit(amount=100.00, currency="USD", payment_method_id='6a23926d-74b6-4373-8434-9d437c2bafb2')
    # res = tb.client.deposit(amount=100.00, currency="USD", payment_method_id='e49c8d15-547b-464e-ac3d-4b9d20b360ec')

    # res = tb.client.crypto_withdraw(amount=1.0, currency="BTC", crypto_address='1JmYrFBLMSCLBwoL87gdQ5Qc9MLvb2egKk')

    # pp(tb.placeBuyOrder())
    # payments = tb.client.get_payment_methods()
    # accounts = tb.client.get_accounts()
    # currencies = tb.client.get_currencies()
    # pp(payments)
    # pp(accounts)
    # pp(currencies)

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