''' Sell Manager Utility'''
from utility import *
from conf.SETTINGS import *


class SellManager():
    def __init__(self, _tradingClient, _assetsDB):
        self.tradingClient = _tradingClient
        self.assetsDB = _assetsDB

    def addAssetEntry(self, assetSymbol):
        self.assetsDB.addAsset(assetSymbol)

    def refreshAssetBalance(self, asset):
        ''' Returns True if asset balance is changed, False if unchanged '''
        return (self.assetsDB.setAssetData(asset['asset'], self.assetsDB.BALANCE_KEY, float(asset['free'])))

    def refreshPurchasePriceAndSettledUptoTradeId(self, assetSymbol):
        settledUptoTradeId = self.assetsDB.getAssetData(assetSymbol, self.assetsDB.SETTLED_UPTO_TRADE_ID_KEY)
        newSettledUptoTradeId = settledUptoTradeId
        totalPricePaid = totalQuantityBought = balanceAssets = effectivePurchasePrice = 0

        trades = self.tradingClient.getTradesFromGivenTradeId((assetSymbol + BASE_ASSET), settledUptoTradeId + 1)
        if trades != None:
            for trade in trades:
                quantity = float(trade['qty'])
                price = float(trade['price'])
                if trade['isBuyer'] is True:
                    totalPricePaid = totalPricePaid + (price * quantity)
                    totalQuantityBought = totalQuantityBought + quantity
                    balanceAssets = balanceAssets + quantity
                else:
                    balanceAssets = balanceAssets - quantity
                if balanceAssets == 0:
                    totalPricePaid = 0
                    totalQuantityBought = 0
                    newSettledUptoTradeId = trade['id']
            if totalQuantityBought != 0:
                effectivePurchasePrice = (totalPricePaid / totalQuantityBought)
            self.assetsDB.setAssetData(assetSymbol, self.assetsDB.SETTLED_UPTO_TRADE_ID_KEY, newSettledUptoTradeId)
            self.assetsDB.setAssetData(assetSymbol, self.assetsDB.EFFECTIVE_PURCHASE_PRICE_KEY, effectivePurchasePrice)

    def refreshAllAssetsBalancesData(self):
        accountInfo = self.tradingClient.getAccountInfo(True)
        allAssets = (accountInfo['balances'])
        for asset in allAssets:
            self.addAssetEntry(asset['asset'])
            if (self.refreshAssetBalance(asset)):
                if self.getAssetPairExchangeInfo(asset['asset'], BASE_ASSET) is not None:
                    self.refreshPurchasePriceAndSettledUptoTradeId(asset['asset'])

    def isAssetPairTradingOnExchange(self, assetPair):
        return ((assetPair['status']) == 'TRADING')

    def isAssetBalanceSellable(self, assetBalance, assetPair):
        for filter in assetPair['filters']:
            if filter['filterType'] == 'LOT_SIZE':
                if (assetBalance >= float(filter['minQty'])):
                    return True
        return False

    def getAssetPairExchangeInfo(self, assetSymbol, baseAsset):
        assetPairsExchangeInfo = self.tradingClient.getExchangeInfo()['symbols']
        assetPairSymbol = assetSymbol + BASE_ASSET
        for assetPairExchangeInfo in assetPairsExchangeInfo:
            if (assetPairExchangeInfo['symbol']) == assetPairSymbol:
                return assetPairExchangeInfo
        return None

    def refreshAssetSellStatus(self, assetSymbol, assetPairExchangeInfo):
        sellStatus = None
        if assetPairExchangeInfo is None:
            sellStatus = self.assetsDB.SELL_STATUS_INVALID_PAIR
        elif self.isAssetPairTradingOnExchange(assetPairExchangeInfo) is False:
            sellStatus = self.assetsDB.SELL_STATUS_NOT_TRADING
        elif self.isAssetBalanceSellable(self.assetsDB.getAssetData(assetSymbol, self.assetsDB.BALANCE_KEY), assetPairExchangeInfo) is False:
            sellStatus = self.assetsDB.SELL_STATUS_LOW_BALANCE
        elif assetSymbol in SELL_BLACKLIST_ASSETS:
            sellStatus = self.assetsDB.SELL_STATUS_BLACKLISTED
        elif self.assetsDB.getAssetData(assetSymbol, self.assetsDB.EFFECTIVE_PURCHASE_PRICE_KEY) == 0:
            sellStatus = self.assetsDB.SELL_STATUS_PURCHASE_PRICE_UNKNOWN
        else:
            sellStatus = self.assetsDB.SELL_STATUS_READY_TO_SELL

        self.assetsDB.setAssetData(assetSymbol, self.assetsDB.SELL_STATUS_KEY, sellStatus)

    def refreshAssetValueData(self, assetSymbol):
        assetData = self.assetsDB.getAssetData(assetSymbol)
        if assetData[self.assetsDB.SELL_STATUS_KEY] in [self.assetsDB.SELL_STATUS_BLACKLISTED, self.assetsDB.SELL_STATUS_PURCHASE_PRICE_UNKNOWN, self.assetsDB.SELL_STATUS_READY_TO_SELL]:
            isProfitLocked = None
            assetPairCurrentValue = self.tradingClient.getSymbolPairTickerPrice(assetSymbol + BASE_ASSET)
            self.assetsDB.setAssetData(assetSymbol, self.assetsDB.CURRENT_VALUE_KEY, assetPairCurrentValue)
            if (assetPairCurrentValue < assetData[self.assetsDB.MIN_VALUE_KEY]):
                assetPairMinValue = assetPairCurrentValue
                self.assetsDB.setAssetData(assetSymbol, self.assetsDB.MIN_VALUE_KEY, assetPairMinValue)
            if (assetPairCurrentValue > assetData[self.assetsDB.MAX_VALUE_KEY]):
                assetPairMaxValue = assetPairCurrentValue
                self.assetsDB.setAssetData(assetSymbol, self.assetsDB.MAX_VALUE_KEY, assetPairMaxValue)
            if (assetData[self.assetsDB.IS_PROFIT_LOCKED_KEY] == False):
                if (assetData[self.assetsDB.CURRENT_VALUE_KEY] > ((100 + GLOBAL_TRAILING_STOP_LOSS_MIN_PROFIT_LOCK) / 100 * assetData[self.assetsDB.EFFECTIVE_PURCHASE_PRICE_KEY])) or (
                        (assetData[self.assetsDB.SELL_STATUS_KEY]) == self.assetsDB.SELL_STATUS_PURCHASE_PRICE_UNKNOWN):
                    isProfitLocked = True
                    self.assetsDB.setAssetData(assetSymbol, self.assetsDB.IS_PROFIT_LOCKED_KEY, isProfitLocked)

    def refreshAllAssetsSellData(self):
        allAssets = self.assetsDB.getAllAssetsList()
        for assetSymbol in allAssets:
            assetPairExchangeInfo = self.getAssetPairExchangeInfo(assetSymbol, BASE_ASSET)
            self.refreshAssetSellStatus(assetSymbol, assetPairExchangeInfo)
            self.refreshAssetValueData(assetSymbol)

    def printAssetsReadyToSell(self, printAssetList):
        import tabulate
        printHeaders = ['SYM', 'Status', 'Quantity', 'PurchasePrice', 'MIN Price (%)', 'CURRENT Price (%)', 'MAX Price (%)', 'isProfitLocked']
        print(tabulate.tabulate(printAssetList, headers=printHeaders, tablefmt='orgtbl', floatfmt=("", "", ".8f", ".8f")))

    def appendAssetToPrintList(self, assetSymbol, assetPrintStringList):
        assetData = self.assetsDB.getAssetData(assetSymbol)
        minPrice = assetData[self.assetsDB.MIN_VALUE_KEY]
        currentPrice = assetData[self.assetsDB.CURRENT_VALUE_KEY]
        maxPrice = assetData[self.assetsDB.MAX_VALUE_KEY]
        effectivePurchasePrice = assetData[self.assetsDB.EFFECTIVE_PURCHASE_PRICE_KEY]
        balance = assetData[self.assetsDB.BALANCE_KEY]
        sellStatus = assetData[self.assetsDB.SELL_STATUS_KEY]
        isProfitLocked = assetData[self.assetsDB.IS_PROFIT_LOCKED_KEY]
        minPricePercentStr = currentPricePercentStr = maxPricePercentStr = " ! "

        if assetData[self.assetsDB.SELL_STATUS_KEY] != self.assetsDB.SELL_STATUS_PURCHASE_PRICE_UNKNOWN:
            minPricePercentStr = "(" + str(fStr(((minPrice - effectivePurchasePrice) / effectivePurchasePrice * 100), 2)) + "%)"
            currentPricePercentStr = "(" + str(fStr(((currentPrice - effectivePurchasePrice) / effectivePurchasePrice * 100), 2)) + "%)"
            maxPricePercentStr = "(" + str(fStr(((maxPrice - effectivePurchasePrice) / effectivePurchasePrice * 100), 2)) + "%)"

        assetPrintStringList.append([assetSymbol, sellStatus, balance, effectivePurchasePrice, fStr(minPrice) + minPricePercentStr, fStr(currentPrice) + currentPricePercentStr, fStr(maxPrice) + maxPricePercentStr, isProfitLocked])

    def printAssetsInfo(self):
        assetPrintStringList = []
        allAssets = self.assetsDB.getAllAssetsList()
        for assetSymbol in allAssets:
            assetSellStatus = self.assetsDB.getAssetData(assetSymbol, self.assetsDB.SELL_STATUS_KEY)
            if assetSellStatus in [self.assetsDB.SELL_STATUS_BLACKLISTED, self.assetsDB.SELL_STATUS_PURCHASE_PRICE_UNKNOWN, self.assetsDB.SELL_STATUS_READY_TO_SELL]:
                self.appendAssetToPrintList(assetSymbol, assetPrintStringList)
        self.printAssetsReadyToSell(assetPrintStringList)

    def sellAsset(self, assetSymbol, assetQuantity):
        msg = "SELLING ASSET : " + assetSymbol
        msg += "\n" + str(self.assetsDB.getAssetData(assetSymbol))
        log(msg)
        self.tradingClient.sellAsset(assetSymbol + BASE_ASSET, assetQuantity)
        self.assetsDB.resetAssetData(assetSymbol, self.assetsDB.MIN_VALUE_KEY)
        self.assetsDB.resetAssetData(assetSymbol, self.assetsDB.MAX_VALUE_KEY)
        self.assetsDB.resetAssetData(assetSymbol, self.assetsDB.IS_PROFIT_LOCKED_KEY)
        sendEmail("SELLING ASSET : " + assetSymbol, msg)

    def sellAssetsReadyToSell(self):
        allAssets = self.assetsDB.getAllAssetsList()
        for assetSymbol in allAssets:
            assetData = self.assetsDB.getAssetData(assetSymbol)
            if assetData[self.assetsDB.SELL_STATUS_KEY] == self.assetsDB.SELL_STATUS_READY_TO_SELL:
                if (assetData[self.assetsDB.CURRENT_VALUE_KEY] < ((100 - GLOBAL_STOP_LOSS) / 100 * assetData[self.assetsDB.EFFECTIVE_PURCHASE_PRICE_KEY])):
                    self.sellAsset(assetSymbol, assetData[self.assetsDB.BALANCE_KEY])
                    return True
                if ((assetData[self.assetsDB.IS_PROFIT_LOCKED_KEY] == True) and (assetData[self.assetsDB.CURRENT_VALUE_KEY] < ((100 - GLOBAL_TRAILING_STOP_LOSS_TAKE_PROFIT) * 100 * assetData[self.assetsDB.MAX_VALUE_KEY]))):
                    self.sellAsset(assetSymbol, assetData[self.assetsDB.BALANCE_KEY])
                    return True