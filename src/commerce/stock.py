import logging

log = logging.getLogger("discord")


class Stock:
    """Stock data object"""

    available: int
    value: int
    ticker: str

    def __init__(self, ticker: str, available: int, value: int):
        self.value = value
        self.available = available
        self.ticker = ticker

    @staticmethod
    def from_dict(dictionary):
        """Constructs a Stock from a dictionary"""
        return Stock(
            str(dictionary["ticker"]),
            int(dictionary["available"]),
            int(dictionary["value"]),
        )
