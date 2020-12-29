from tradingClient import TradingClient
from assetsDatabase import AssetsDatabase
from sellManager import SellManager
from buyManager import BuyManager

from utility import *
from conf.SETTINGS import *


def bot_main():
    log("Inside bot_main()")
    trading_client = TradingClient()
    assets_db = AssetsDatabase(ASSETS_DB_FILE_NAME)
    sell_manager = SellManager(trading_client, assets_db)
    buy_manager = BuyManager(trading_client, assets_db)
    count = -1
    while True:
        count = count + 1
        if trading_client.is_server_up():
            if (count % 3600) == 0:  # Every hour
                trading_client.get_exchange_info(True)
            if (count % 10) == 0:  # Every 10 seconds
                sell_manager.refresh_all_assets_balances_data()
            sell_manager.refresh_all_assets_sell_data()
            clear_screen()
            print(get_system_date_time())
            sell_manager.print_assets_info()
            if BUYING_ENABLE:
                buy_manager.buy()
            if SELLING_ENABLE:
                if sell_manager.sell_assets_ready_to_sell():
                    sleep(10)
                    count = -1
        sleep(DELAY_IN_EACH_CYCLE)


bot_main()
log("BOT TERMINATED !")
