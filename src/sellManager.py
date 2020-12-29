""" Sell Manager Utility"""
from conf.SETTINGS import *
from utility import *


class SellManager:
    def __init__(self, _trading_client, _assets_db):
        self.tradingClient = _trading_client
        self.assetsDB = _assets_db

    def add_asset_entry(self, asset_symbol):
        self.assetsDB.add_asset(asset_symbol)

    def refresh_asset_balance(self, asset):
        """ Returns True if asset balance is changed, False if unchanged """
        return self.assetsDB.set_asset_data(asset['asset'], self.assetsDB.BALANCE_KEY, float(asset['free']))

    def refresh_purchase_price_and_settled_upto_trade_id(self, asset_symbol):
        settled_upto_trade_id = self.assetsDB.get_asset_data(asset_symbol, self.assetsDB.SETTLED_UPTO_TRADE_ID_KEY)
        new_settled_upto_trade_id = settled_upto_trade_id
        total_price_paid = total_quantity_bought = balance_assets = effective_purchase_price = 0

        trades = self.tradingClient.get_trades_from_given_trade_id((asset_symbol + BASE_ASSET),
                                                                   settled_upto_trade_id + 1)
        if trades is not None:
            for trade in trades:
                quantity = float(trade['qty'])
                price = float(trade['price'])
                if trade['isBuyer'] is True:
                    total_price_paid = total_price_paid + (price * quantity)
                    total_quantity_bought = total_quantity_bought + quantity
                    balance_assets = balance_assets + quantity
                else:
                    balance_assets = balance_assets - quantity
                if balance_assets == 0:
                    total_price_paid = 0
                    total_quantity_bought = 0
                    new_settled_upto_trade_id = trade['id']
            if total_quantity_bought != 0:
                effective_purchase_price = (total_price_paid / total_quantity_bought)
            self.assetsDB.set_asset_data(asset_symbol, self.assetsDB.SETTLED_UPTO_TRADE_ID_KEY,
                                         new_settled_upto_trade_id)
            self.assetsDB.set_asset_data(asset_symbol, self.assetsDB.EFFECTIVE_PURCHASE_PRICE_KEY,
                                         effective_purchase_price)

    def refresh_all_assets_balances_data(self):
        account_info = self.tradingClient.get_account_info(True)
        all_assets = (account_info['balances'])
        for asset in all_assets:
            self.add_asset_entry(asset['asset'])
            if self.refresh_asset_balance(asset):
                if self.get_asset_pair_exchange_info(asset['asset'], BASE_ASSET) is not None:
                    self.refresh_purchase_price_and_settled_upto_trade_id(asset['asset'])

    @staticmethod
    def is_asset_pair_trading_on_exchange(asset_pair):
        return (asset_pair['status']) == 'TRADING'

    @staticmethod
    def is_asset_balance_sellable(asset_balance, asset_pair):
        for _filter in asset_pair['filters']:
            if _filter['filterType'] == 'LOT_SIZE':
                if asset_balance >= float(_filter['minQty']):
                    return True
        return False

    def get_asset_pair_exchange_info(self, asset_symbol, base_asset):
        asset_pairs_exchange_info = self.tradingClient.get_exchange_info()['symbols']
        asset_pair_symbol = asset_symbol + base_asset
        for assetPairExchangeInfo in asset_pairs_exchange_info:
            if (assetPairExchangeInfo['symbol']) == asset_pair_symbol:
                return assetPairExchangeInfo
        return None

    def refresh_asset_sell_status(self, asset_symbol, asset_pair_exchange_info):
        if asset_pair_exchange_info is None:
            sell_status = self.assetsDB.SELL_STATUS_INVALID_PAIR
        elif self.is_asset_pair_trading_on_exchange(asset_pair_exchange_info) is False:
            sell_status = self.assetsDB.SELL_STATUS_NOT_TRADING
        elif self.is_asset_balance_sellable(self.assetsDB.get_asset_data(asset_symbol, self.assetsDB.BALANCE_KEY),
                                            asset_pair_exchange_info) is False:
            sell_status = self.assetsDB.SELL_STATUS_LOW_BALANCE
        elif asset_symbol in SELL_BLOCKED_ASSETS_LIST:
            sell_status = self.assetsDB.SELL_STATUS_BLOCKED
        elif self.assetsDB.get_asset_data(asset_symbol, self.assetsDB.EFFECTIVE_PURCHASE_PRICE_KEY) == 0:
            sell_status = self.assetsDB.SELL_STATUS_PURCHASE_PRICE_UNKNOWN
        else:
            sell_status = self.assetsDB.SELL_STATUS_READY_TO_SELL

        self.assetsDB.set_asset_data(asset_symbol, self.assetsDB.SELL_STATUS_KEY, sell_status)

    def refresh_asset_value_data(self, asset_symbol):
        asset_data = self.assetsDB.get_asset_data(asset_symbol)
        if asset_data[self.assetsDB.SELL_STATUS_KEY] in [self.assetsDB.SELL_STATUS_BLOCKED,
                                                         self.assetsDB.SELL_STATUS_PURCHASE_PRICE_UNKNOWN,
                                                         self.assetsDB.SELL_STATUS_READY_TO_SELL]:
            asset_pair_current_value = self.tradingClient.get_symbol_pair_ticker_price(asset_symbol + BASE_ASSET)
            self.assetsDB.set_asset_data(asset_symbol, self.assetsDB.CURRENT_VALUE_KEY, asset_pair_current_value)
            if asset_pair_current_value < asset_data[self.assetsDB.MIN_VALUE_KEY]:
                asset_pair_min_value = asset_pair_current_value
                self.assetsDB.set_asset_data(asset_symbol, self.assetsDB.MIN_VALUE_KEY, asset_pair_min_value)
            if asset_pair_current_value > asset_data[self.assetsDB.MAX_VALUE_KEY]:
                asset_pair_max_value = asset_pair_current_value
                self.assetsDB.set_asset_data(asset_symbol, self.assetsDB.MAX_VALUE_KEY, asset_pair_max_value)
            if not asset_data[self.assetsDB.IS_PROFIT_LOCKED_KEY]:
                if (asset_data[self.assetsDB.CURRENT_VALUE_KEY] > (
                        (100 + GLOBAL_TRAILING_STOP_LOSS_MIN_PROFIT_LOCK) / 100 * asset_data[
                    self.assetsDB.EFFECTIVE_PURCHASE_PRICE_KEY])) or (
                        (
                                asset_data[
                                    self.assetsDB.SELL_STATUS_KEY]) == self.assetsDB.SELL_STATUS_PURCHASE_PRICE_UNKNOWN):
                    is_profit_locked = True
                    self.assetsDB.set_asset_data(asset_symbol, self.assetsDB.IS_PROFIT_LOCKED_KEY, is_profit_locked)

    def refresh_all_assets_sell_data(self):
        all_assets = self.assetsDB.get_all_assets_list()
        for assetSymbol in all_assets:
            asset_pair_exchange_info = self.get_asset_pair_exchange_info(assetSymbol, BASE_ASSET)
            self.refresh_asset_sell_status(assetSymbol, asset_pair_exchange_info)
            self.refresh_asset_value_data(assetSymbol)

    @staticmethod
    def print_assets_ready_to_sell(print_asset_list):
        import tabulate
        print_headers = ['SYM', 'Status', 'Quantity', 'PurchasePrice', 'MIN Price (%)', 'CURRENT Price (%)',
                         'MAX Price (%)', 'isProfitLocked']
        print(
            tabulate.tabulate(print_asset_list, headers=print_headers, tablefmt='orgtbl',
                              floatfmt=("", "", ".8f", ".8f")))

    def append_asset_to_print_list(self, asset_symbol, asset_print_string_list):
        asset_data = self.assetsDB.get_asset_data(asset_symbol)
        min_price = asset_data[self.assetsDB.MIN_VALUE_KEY]
        current_price = asset_data[self.assetsDB.CURRENT_VALUE_KEY]
        max_price = asset_data[self.assetsDB.MAX_VALUE_KEY]
        effective_purchase_price = asset_data[self.assetsDB.EFFECTIVE_PURCHASE_PRICE_KEY]
        balance = asset_data[self.assetsDB.BALANCE_KEY]
        sell_status = asset_data[self.assetsDB.SELL_STATUS_KEY]
        is_profit_locked = asset_data[self.assetsDB.IS_PROFIT_LOCKED_KEY]
        min_price_percent_str = current_price_percent_str = max_price_percent_str = " ! "

        if asset_data[self.assetsDB.SELL_STATUS_KEY] != self.assetsDB.SELL_STATUS_PURCHASE_PRICE_UNKNOWN:
            min_price_percent_str = "(" + str(
                f_str(((min_price - effective_purchase_price) / effective_purchase_price * 100), 2)) + "%)"
            current_price_percent_str = "(" + str(
                f_str(((current_price - effective_purchase_price) / effective_purchase_price * 100), 2)) + "%)"
            max_price_percent_str = "(" + str(
                f_str(((max_price - effective_purchase_price) / effective_purchase_price * 100), 2)) + "%)"

        asset_print_string_list.append(
            [asset_symbol, sell_status, balance, effective_purchase_price, f_str(min_price) + min_price_percent_str,
             f_str(current_price) + current_price_percent_str, f_str(max_price) + max_price_percent_str,
             is_profit_locked])

    def print_assets_info(self):
        asset_print_string_list = []
        all_assets = self.assetsDB.get_all_assets_list()
        for assetSymbol in all_assets:
            if assetSymbol == 'BNB':
                continue
            asset_sell_status = self.assetsDB.get_asset_data(assetSymbol, self.assetsDB.SELL_STATUS_KEY)
            if asset_sell_status in [self.assetsDB.SELL_STATUS_BLOCKED,
                                     self.assetsDB.SELL_STATUS_PURCHASE_PRICE_UNKNOWN,
                                     self.assetsDB.SELL_STATUS_READY_TO_SELL]:
                self.append_asset_to_print_list(assetSymbol, asset_print_string_list)
        self.print_assets_ready_to_sell(asset_print_string_list)

    def sell_asset(self, asset_symbol, asset_quantity):
        msg = "SELLING ASSET : " + asset_symbol
        msg += "\n" + str(self.assetsDB.get_asset_data(asset_symbol))
        log(msg)
        self.tradingClient.sell_asset(asset_symbol + BASE_ASSET, asset_quantity)
        self.assetsDB.reset_asset_data(asset_symbol, self.assetsDB.MIN_VALUE_KEY)
        self.assetsDB.reset_asset_data(asset_symbol, self.assetsDB.MAX_VALUE_KEY)
        self.assetsDB.reset_asset_data(asset_symbol, self.assetsDB.IS_PROFIT_LOCKED_KEY)
        send_email("SELLING ASSET : " + asset_symbol, msg)

    def sell_assets_ready_to_sell(self):
        all_assets = self.assetsDB.get_all_assets_list()
        for assetSymbol in all_assets:
            asset_data = self.assetsDB.get_asset_data(assetSymbol)
            if asset_data[self.assetsDB.SELL_STATUS_KEY] == self.assetsDB.SELL_STATUS_READY_TO_SELL:
                if asset_data[self.assetsDB.CURRENT_VALUE_KEY] < (
                        (100 - GLOBAL_STOP_LOSS) / 100 * asset_data[self.assetsDB.EFFECTIVE_PURCHASE_PRICE_KEY]):
                    self.sell_asset(assetSymbol, asset_data[self.assetsDB.BALANCE_KEY])
                    return True
                if (asset_data[self.assetsDB.IS_PROFIT_LOCKED_KEY] is True) and (
                        asset_data[self.assetsDB.CURRENT_VALUE_KEY] < (
                        (100 - GLOBAL_TRAILING_STOP_LOSS_TAKE_PROFIT) / 100 * asset_data[self.assetsDB.MAX_VALUE_KEY])):
                    self.sell_asset(assetSymbol, asset_data[self.assetsDB.BALANCE_KEY])
                    return True
