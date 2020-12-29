from tradingClient import TradingClient
from assetsDatabase import AssetsDatabase
from sellManager import SellManager
from buyManager import BuyManager

from utility import *
from conf.SETTINGS import *

def botMain():
    log("Inside botMain()")
    tradingClient = TradingClient()
    assetsDB = AssetsDatabase(ASSETS_DB_FILE_NAME)
    sellManager = SellManager(tradingClient, assetsDB)
    buyManager = BuyManager(tradingClient, assetsDB)
    count = -1
    while True:
        count = count + 1
        if tradingClient.isServerUp():
            if((count % 3600) == 0): #Every hour
                tradingClient.getExchangeInfo(True)
            if ((count % 10) == 0):  # Every 10 seconds
                sellManager.refreshAllAssetsBalancesData()
            sellManager.refreshAllAssetsSellData()
            clearScreen()
            print(getSystemDateTime())
            sellManager.printAssetsInfo()
            if BUYING_ENABLE:
                buyManager.buy()
            if SELLING_ENABLE:
                if sellManager.sellAssetsReadyToSell():
                    sleep(10)
                    count = -1
        sleep(DELAY_IN_EACH_CYCLE)

botMain()
log("BOT TERMINATED !")