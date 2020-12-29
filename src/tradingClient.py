from binance.client import Client
from conf.SECRETS import API_KEY, API_SECRET
from utility import *


class TradingClient:
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

    def get_exchange_info(self, is_refresh_requested=False):
        if is_refresh_requested:
            while True:
                try:
                    self.exchangeInfo = self.client.get_exchange_info()
                    break
                except:
                    log("EXCEPTION : refreshExchangeInfo")
                    sleep(self.INTER_ATTEMPT_DELAY)
        return self.exchangeInfo

    def get_account_info(self, is_refresh_requested=False):
        if is_refresh_requested:
            while True:
                try:
                    self.accountInfo = self.client.get_account()
                    break
                except:
                    log("EXCEPTION : get_account_info")
                    sleep(self.INTER_ATTEMPT_DELAY)
        return self.accountInfo

    def is_server_up(self):
        while True:
            try:
                status = self.client.get_system_status()
                return status['status'] is 0
            except:
                log("EXCEPTION : is_server_up")
                sleep(self.INTER_ATTEMPT_DELAY)

    def sell_asset(self, asset_pair, asset_quantity):
        while True:
            try:
                self.client.order_market_sell(symbol=asset_pair, quantity=asset_quantity)
                break
            except:
                log("EXCEPTION : sell_asset " + str(asset_pair) + ", Qty :" + str(asset_quantity))
                sleep(self.INTER_ATTEMPT_DELAY)

    def get_symbol_pair_ticker_price(self, symbol_pair):
        while True:
            try:
                symbol_ticker_price = self.client.get_symbol_ticker(symbol=symbol_pair)
                return float(symbol_ticker_price['price'])
            except:
                log("EXCEPTION : get_symbol_pair_ticker_price ")
                sleep(self.INTER_ATTEMPT_DELAY)

    def get_trades_from_given_trade_id(self, symbol_pair, from_trade_id=0):
        while True:
            try:
                trades = self.client.get_my_trades(symbol=symbol_pair, fromId=from_trade_id)
                return trades
            except:
                log("EXCEPTION : get_trades_from_given_trade_id ")
                sleep(self.INTER_ATTEMPT_DELAY)
