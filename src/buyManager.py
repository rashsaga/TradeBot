""" Buy Manager Utility"""


class BuyManager:
    tradingClient = None
    assetsDB = None

    def __init__(self, _trading_client, _assets_db):
        self.tradingClient = _trading_client
        self.assetsDB = _assets_db

    def buy(self):
        return
