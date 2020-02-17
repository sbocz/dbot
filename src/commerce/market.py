import logging
import os
import random

from dotenv import load_dotenv
from scipy import stats
from src.commerce.bank import Bank
from src.commerce.stock import Stock
from src.commerce.stock_holding import StockHolding
from src.utility import read_json_from_file, write_json_to_file

log = logging.getLogger('discord')
load_dotenv()
STOCKS_FILE = os.path.join(os.getenv('BRAIN_PATH'), 'stocks.json')
STOCK_HOLDINGS_FILE = os.path.join(os.getenv('BRAIN_PATH'), 'stock_holdings.json')
MAX_BASE_VOLATILITY = 0.2
TETHER = 400
MAX_TETHER_VOLATILITY = 0.15
MAX_PERCENTILE_FOR_BIG_SWING = 0.7
BIG_SWING_MIN = 10
BIG_SWING_MAX = 30
BIG_SWING_CHANCE = 0.05
TETHER_SWING_CHANCE = 0.15
MAX_STOCKS = 10


def rand():
    return random.random()


class Market:
    def __init__(self):
        self.stocks = self.load_stocks(STOCKS_FILE)
        self.stock_holdings = self.load_stock_holdings(STOCK_HOLDINGS_FILE)
        self.tether = TETHER
        self.MAX_STOCKS = MAX_STOCKS

    @staticmethod
    def load_stocks(filename):
        json_list = read_json_from_file(filename)
        stocks = []
        for d in json_list:
            stock = Stock.from_dict(d)
            stocks.append(stock)
        return stocks

    def save_stocks(self):
        stock_list = []
        for stock in self.stocks:
            stock_list.append(stock.__dict__)
        write_json_to_file(STOCKS_FILE, stock_list)

    @staticmethod
    def load_stock_holdings(filename):
        json_list = read_json_from_file(filename)
        stock_holdings = []
        for d in json_list:
            stock_holdings.append(StockHolding.from_dict(d))
        return stock_holdings

    def save_stock_holdings(self):
        stock_holdings_list = []
        for holding in self.stock_holdings:
            stock_holdings_list.append(holding.__dict__)
        write_json_to_file(STOCK_HOLDINGS_FILE, stock_holdings_list)

    @staticmethod
    def big_swing(stocks, price):
        stock_values = [stock.value for stock in stocks]
        position = stats.percentileofscore(stock_values, price) / 100
        need_for_pos = MAX_PERCENTILE_FOR_BIG_SWING - position
        percent_swing = (BIG_SWING_MIN + (rand() * (BIG_SWING_MAX - BIG_SWING_MIN))) / 100
        price_change = price * percent_swing
        if rand() < need_for_pos or rand() > 0.5:
            return price_change
        else:
            return -1 * price_change

    @staticmethod
    def tether_swing(price, tether):
        change = rand() * MAX_TETHER_VOLATILITY
        if price > tether:
            return -1 * change
        return change

    @staticmethod
    def normal_swing(price):
        volatility_ratio = rand()
        volatility = volatility_ratio * MAX_BASE_VOLATILITY
        # Avg < 0
        rand_change = (rand() * 2) - 1.1
        volatility_mod = ((volatility_ratio * 2.0) * (volatility_ratio * 2.0) / 100.0)
        return ((rand_change * volatility) + volatility_mod) * price

    def get_change(self, price):
        if random.random() < BIG_SWING_CHANCE:
            return self.big_swing(self.stocks, price)
        elif random.random() < TETHER_SWING_CHANCE:
            return self.tether_swing(price, TETHER)
        else:
            return self.normal_swing(price)

    def update_holding(self, account_id: int, ticker: str, change: int):
        existing_holding = next(filter(lambda stock_holding: stock_holding.owner_id == account_id and stock_holding.ticker == ticker, self.stock_holdings), None)
        if existing_holding is None:
            self.stock_holdings.append(StockHolding(ticker, account_id, change))
        else:
            existing_holding.quantity += change
        self.save_stock_holdings()

    def get_holding(self, account_id: int, ticker: str) -> StockHolding:
        return next(filter(lambda stock_holding: stock_holding.owner_id == account_id and stock_holding.ticker == ticker, self.stock_holdings), None)

    def get_holdings(self, account_id: int):
        return list(filter(lambda stock_holding: stock_holding.owner_id == account_id, self.stock_holdings))

    def get_stock(self, ticker: str) -> Stock:
        return next(filter(lambda stock: stock.ticker == ticker, self.stocks), None)
