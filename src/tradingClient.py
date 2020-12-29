from binance.client import Client
from conf.SECRETS import API_KEY, API_SECRET
from utility import *

class TradingClient():
    def __init__(self):
        self.client = None
        self.exchangeInfo = None
        self.accountInfo = None
        self.INTER_ATTEMPT_DELAY = 0.5  # Seconds
        while True:
            try:
                self.client = Client(API_KEY, API_SECRET)
                break
            except:
                log("EXCEPTION : establishConnection")
                sleep(self.INTER_ATTEMPT_DELAY)

    def getExchangeInfo(self, isRefreshRequested = False):
        if isRefreshRequested:
            while True:
                try:
                    self.exchangeInfo = self.client.get_exchange_info()
                    break
                except:
                    log("EXCEPTION : refreshExchangeInfo")
                    sleep(self.INTER_ATTEMPT_DELAY)
        return self.exchangeInfo

    def getAccountInfo(self, isRefreshRequested = False):
        if isRefreshRequested:
            while True:
                try:
                    self.accountInfo = self.client.get_account()
                    break
                except:
                    log("EXCEPTION : getAccountInfo")
                    sleep(self.INTER_ATTEMPT_DELAY)
        return self.accountInfo

    def isServerUp(self):
        while True:
            try:
                status = self.client.get_system_status()
                return (status['status'] is 0)
            except:
                log("EXCEPTION : isServerUp")
                sleep(self.INTER_ATTEMPT_DELAY)

    def sellAsset(self, assetPair, assetQuantity):
        while True:
            try:
                self.client.order_market_sell(symbol=assetPair, quantity=assetQuantity)
                break
            except:
                log("EXCEPTION : sellAsset " + str(assetPair) + ", Qty :" + str(assetQuantity))
                sleep(self.INTER_ATTEMPT_DELAY)

    def getSymbolPairTickerPrice(self, symbolPair):
        while True:
            try:
                symbolTickerPrice = self.client.get_symbol_ticker(symbol=symbolPair)
                return float(symbolTickerPrice['price'])
            except:
                log("EXCEPTION : getSymbolPairTickerPrice ")
                sleep(self.INTER_ATTEMPT_DELAY)

    def getTradesFromGivenTradeId(self, symbolPair, fromTradeId = 0):
        while True:
            try:
                trades = self.client.get_my_trades(symbol=symbolPair, fromId=fromTradeId)
                return trades
            except:
                log("EXCEPTION : getTradesFromGivenTradeId ")
                sleep(self.INTER_ATTEMPT_DELAY)