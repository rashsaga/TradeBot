''' Buy Manager Utility'''

class BuyManager():
    tradingClient = None
    assetsDB = None

    def __init__(self, _tradingClient, _assetsDB):
        self.tradingClient = _tradingClient
        self.assetsDB = _assetsDB

    def buy(self):
        return