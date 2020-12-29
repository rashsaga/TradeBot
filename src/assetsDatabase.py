import pickledb
import sys


class AssetsDatabase:
    # Persistent key value pair
    SETTLED_UPTO_TRADE_ID_KEY = 'settledUptoTradeId'
    MIN_VALUE_KEY = 'minValue'
    MAX_VALUE_KEY = 'maxValue'
    IS_PROFIT_LOCKED_KEY = 'isProfitLocked'
    BALANCE_KEY = 'balance'
    PERSISTENT_KEYS_DEFAULT_VALUE = {SETTLED_UPTO_TRADE_ID_KEY: 0,
                                     MIN_VALUE_KEY: sys.maxsize,
                                     MAX_VALUE_KEY: 0,
                                     IS_PROFIT_LOCKED_KEY: False,
                                     BALANCE_KEY: 0}

    # Other key value pair
    CURRENT_VALUE_KEY = 'currentValue'
    EFFECTIVE_PURCHASE_PRICE_KEY = 'effectivePurchasePrice'
    SELL_STATUS_KEY = 'sellStatus'

    SELL_STATUS_INVALID_PAIR = 'PAIR!'
    SELL_STATUS_NOT_TRADING = 'DOWN'
    SELL_STATUS_LOW_BALANCE = 'LOW'
    SELL_STATUS_BLACKLISTED = 'BLOCK'
    SELL_STATUS_PURCHASE_PRICE_UNKNOWN = 'FREE!'
    SELL_STATUS_READY_TO_SELL = 'READY'

    VOLATILE_KEYS_DEFAULT_VALUE = {CURRENT_VALUE_KEY: 0,
                                   EFFECTIVE_PURCHASE_PRICE_KEY: 0,
                                   SELL_STATUS_KEY: SELL_STATUS_BLACKLISTED}

    def __init__(self, assets_db_file_name):
        self.assetsDB = pickledb.load(assets_db_file_name, False)

    def get_asset_data(self, asset_symbol, key=None):
        asset_data = self.assetsDB.get(asset_symbol)
        return asset_data if (key is None) else (asset_data[key])

    def set_asset_data(self, asset_symbol, key, value):
        is_value_changed = False
        value_in_db = self.assetsDB.get(asset_symbol)[key]
        if value_in_db is False or value_in_db != value:
            self.assetsDB.set(asset_symbol)[key] = value
            is_value_changed = True
            if key in self.PERSISTENT_KEYS_DEFAULT_VALUE:
                self.assetsDB.dump()
        return is_value_changed

    def reset_asset_data(self, asset_symbol, key):
        self.set_asset_data(asset_symbol, key, self.PERSISTENT_KEYS_DEFAULT_VALUE[key])

    def add_asset(self, asset_symbol):
        if self.get_asset_data(asset_symbol) is None:
            self.assetsDB.set(asset_symbol, {**self.PERSISTENT_KEYS_DEFAULT_VALUE, **self.VOLATILE_KEYS_DEFAULT_VALUE})
            self.assetsDB.dump()

    def get_all_assets_list(self):
        return self.assetsDB.getall()
