import logging

log = logging.getLogger("discord")


class StockHolding:
    owner_id: int
    quantity: int
    ticker: str

    def __init__(self, ticker: str, owner_id: int, quantity: int):
        self.owner_id = owner_id
        self.quantity = quantity
        self.ticker = ticker

    @staticmethod
    def from_dict(d):
        return StockHolding(str(d["ticker"]), int(d["owner_id"]), int(d["quantity"]))
