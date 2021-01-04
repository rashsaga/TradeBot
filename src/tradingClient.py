from binance.client import Client
from conf.SECRETS import API_KEY, API_SECRET
from utility import *


class TradingClient:
    def __init__(self):
        self.client = None
        self.exchangeInfoCache = None
        self.accountInfo = None
        self.INTER_ATTEMPT_DELAY = 0.5  # Seconds
        while True:
            try:
                self.client = Client(API_KEY, API_SECRET)
                break
            except Exception as e:
                log("EXCEPTION : establishConnection : " + str(e))
                sleep(self.INTER_ATTEMPT_DELAY)

    def refresh_exchange_info_cache(self):
        while True:
            try:
                self.exchangeInfoCache = self.client.get_exchange_info()
                self.exchangeInfoCache['_symbols'] = {i['symbol']:i for i in self.exchangeInfoCache['symbols']}
                break
            except Exception as e:
                log("EXCEPTION : refreshExchangeInfo : " + str(e))
                sleep(self.INTER_ATTEMPT_DELAY)

    def get_exchange_info_cache(self):
        return self.exchangeInfoCache

    def get_account_info(self, is_refresh_requested=False):
        if is_refresh_requested:
            while True:
                try:
                    self.accountInfo = self.client.get_account()
                    break
                except Exception as e:
                    log("EXCEPTION : get_account_info : " + str(e))
                    sleep(self.INTER_ATTEMPT_DELAY)
        return self.accountInfo

    def is_server_up(self):
        while True:
            try:
                status = self.client.get_system_status()
                return status['status'] == 0
            except Exception as e:
                log("EXCEPTION : is_server_up : " + str(e))
                sleep(self.INTER_ATTEMPT_DELAY)

    def sell_asset(self, asset_pair, asset_quantity):
        asset_quantity = self.get_rounded_quantity_exchange_support(asset_pair, asset_quantity)
        while True:
            try:
                self.client.order_market_sell(symbol=asset_pair, quantity=asset_quantity)
                break
            except Exception as e:
                log("EXCEPTION : sell_asset " + str(asset_pair) + ", Qty :" + str(asset_quantity) + " : " + str(e))
                sleep(self.INTER_ATTEMPT_DELAY)

    def get_asset_pair_ticker_price(self, asset_pair):
        while True:
            try:
                symbol_ticker_price = self.client.get_symbol_ticker(symbol=asset_pair)
                return float(symbol_ticker_price['price'])
            except Exception as e:
                log("EXCEPTION : get_asset_pair_ticker_price : " + str(e))
                sleep(self.INTER_ATTEMPT_DELAY)

    def get_trades_from_given_trade_id(self, asset_pair, from_trade_id=0):
        while True:
            try:
                trades = self.client.get_my_trades(symbol=asset_pair, fromId=from_trade_id)
                return trades
            except Exception as e:
                log("EXCEPTION : get_trades_from_given_trade_id : " + str(e))
                sleep(self.INTER_ATTEMPT_DELAY)

    def get_asset_pair_exchange_info(self, asset_pair):
        return self.get_exchange_info_cache()['_symbols'].get(asset_pair)

    def get_rounded_quantity_exchange_support(self, asset_pair, quantity):
        asset_pair_exchange_info = self.get_asset_pair_exchange_info(asset_pair)
        if asset_pair_exchange_info:
            for _filter in asset_pair_exchange_info['filters']:
                if _filter['filterType'] == 'LOT_SIZE':
                    return dumb_truncate(quantity, _filter['stepSize'])
        return quantity
