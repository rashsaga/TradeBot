import pickledb3
import sys

class AssetsDatabase():
    #Persistent key value pair
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

    #Other key value pair
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

    def __init__(self, assetsDBFileName):
        self.assetsDB = pickledb3.load(assetsDBFileName, False)

    def getAssetData(self, assetSymbol, key = None):
        assetData = self.assetsDB.get(assetSymbol)
        return (assetData if (key == None) else (assetData[key]))

    def setAssetData(self, assetSymbol, key, value):
        isValueChanged = False
        if ((self.assetsDB.get(assetSymbol)[key]) != value):
            self.assetsDB.get(assetSymbol)[key] = value
            isValueChanged = True
            if(key in self.PERSISTENT_KEYS_DEFAULT_VALUE):
                self.assetsDB.dump()
        return isValueChanged

    def resetAssetData(self, assetSymbol, key):
        self.setAssetData(assetSymbol, key, self.PERSISTENT_KEYS_DEFAULT_VALUE[key])

    def addAsset(self, assetSymbol):
        if self.getAssetData(assetSymbol) == None:
            self.assetsDB.set(assetSymbol, {**self.PERSISTENT_KEYS_DEFAULT_VALUE, **self.VOLATILE_KEYS_DEFAULT_VALUE})
            self.assetsDB.dump()

    def getAllAssetsList(self):
        return self.assetsDB.getall()