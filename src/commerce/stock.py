import logging

log = logging.getLogger('discord')


class Stock:
    available: int
    value: int
    ticker: str

    def __init__(self, ticker: str, available: int, value: int):
        self.value = value
        self.available = available
        self.ticker = ticker

    @staticmethod
    def from_dict(d):
        return Stock(str(d['ticker']), int(d['available']), int(d['value']))
