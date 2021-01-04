########################################################################################################################
""" Settings for bot """
########################################################################################################################

''' GENERAL SETTINGS '''
ASSETS_DB_FILE_NAME = '../db/assetsData.json'

''' TRADING-SPECIFIC SETTINGS '''
BASE_ASSET = 'USDT'
DELAY_IN_EACH_CYCLE = 1  # seconds

''' BUY MANAGER - INPUTS '''
BUYING_ENABLE = False
BUY_BLOCKED_ASSETS_LIST = [BASE_ASSET]

''' SELL MANAGER - INPUTS '''
SELLING_ENABLE = True
SELL_BLOCKED_ASSETS_LIST = ['BNB']
GLOBAL_STOP_LOSS = 4
GLOBAL_TRAILING_STOP_LOSS_MIN_PROFIT_LOCK = 4
GLOBAL_TRAILING_STOP_LOSS_TAKE_PROFIT = 2.5
