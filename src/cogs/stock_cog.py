import logging
import random
from operator import itemgetter

import discord
from discord.ext import commands, tasks

from src.commerce.bank import Bank
from src.commerce.market import Market
from src.commerce.stock import Stock
from src.commerce.stock_holding import StockHolding

log = logging.getLogger('discord')

STOCK_CREATION_PRICE = 1000
STOCK_STARTING_PRICE = 100
STOCK_STARTING_AVAILABILITY = 100


def rand():
    return random.random()


class StockCog(commands.Cog, name='stock'):
    def __init__(self, bot: commands.Bot, bank: Bank, market: Market):
        self.market = market
        self.bank = bank
        self.bot = bot
        self._last_member = None

    @tasks.loop(minutes=43.0)
    async def randomize_stocks(self):
        log.info("Randomizing Stocks")
        for stock in self.market.stocks:
            stock.value += int(self.market.get_change(stock.value))
        self.market.save_stocks()

    @commands.Cog.listener()
    async def on_ready(self):
        self.randomize_stocks.start()

    @commands.command(name='invest')
    async def invest(self, ctx, stock_ticker: str, quantity: int = 1):
        """See stock buy command."""
        await self._buy(ctx, stock_ticker, quantity)

    @commands.command(name='divest')
    async def divest(self, ctx, stock_ticker: str, quantity: int = 1):
        """See stock sell command."""
        await self._sell(ctx, stock_ticker, quantity)

    @commands.group(name='stock')
    async def stock(self, ctx):
        """
        Interact with the stock market
        """
        if ctx.invoked_subcommand is None:
            await ctx.send(f'stock "{ctx.subcommand_passed}" is not a command')

    @stock.command(name='help')
    async def _help(self, ctx):
        """
        HELP
        """
        await ctx.send_help(ctx.command.parent)

    @stock.command(name='buy')
    async def _buy(self, ctx, stock_ticker: str, quantity: int = 1):
        """
        Buy stock
        """
        user_id = ctx.author.id
        account = self.bank.get_account(user_id)
        if account is None:
            await ctx.send(f'Hmmm, looks like you don\'t have an account yet.')
            return
        stock = next(filter(lambda s: s.ticker == stock_ticker, self.market.stocks), None)
        if stock is None:
            await ctx.send(f'Stock with ticker {stock_ticker} does not exist.')
            return
        if quantity < 0:
            await ctx.send(f'No.')
            return
        if account.value < stock.value * quantity:
            await ctx.send(f'You do not have enough dbucks to buy {quantity} stocks of {stock_ticker}')
            return
        if stock.available < quantity:
            await ctx.send(f'There are not enough stocks of {stock_ticker} on the market ({stock.available} available)')
            return
        else:
            # Update stock
            stock.available -= quantity
            self.market.save_stocks()

            # Update holding
            self.market.update_holding(account.account_id, stock.ticker, quantity)

            # Update account
            self.bank.make_payment(account.account_id, stock.value * quantity)

            await ctx.send(
                f"You have purchased {quantity} shares of {stock_ticker} for {stock.value * quantity} dbucks!")

    @stock.command(name='sell')
    async def _sell(self, ctx, stock_ticker: str, quantity: int = 1):
        """
        Sell stock
        """
        user_id = ctx.author.id
        account = self.bank.get_account(user_id)
        if account is None:
            await ctx.send(f'Hmmm, looks like you don\'t have an account yet.')
            return
        stock = next(filter(lambda s: s.ticker == stock_ticker, self.market.stocks), None)
        if stock is None:
            await ctx.send(f'Stock with ticker {stock_ticker} does not exist.')
            return
        if quantity < 0:
            await ctx.send(f'No.')
            return
        holding = self.market.get_holding(account.account_id, stock.ticker)
        if holding is None or holding.quantity < quantity:
            await ctx.send(f'You do not have enough {stock_ticker}')
            return
        else:
            # Update stock
            stock.available += quantity
            self.market.save_stocks()

            # Update holding
            self.market.update_holding(account.account_id, stock.ticker, -1 * quantity)

            # Update account
            self.bank.receive_payment(account.account_id, stock.value * quantity)

            await ctx.send(
                f"You have sold {quantity} shares of {stock_ticker} for {stock.value * quantity} dbucks!")

    @stock.command(name='holdings')
    async def _holdings(self, ctx, member: discord.Member = None):
        """
        List stock holdings
        """
        result = ''
        is_self = False
        if member is None:
            is_self = True
            user_id = ctx.author.id
        else:
            user_id = member.id
        user: discord.User = self.bot.get_user(user_id)
        holdings = self.market.get_holdings(user_id)

        if holdings is not None and len(holdings) > 0:
            holding: StockHolding
            for holding in holdings:
                stock_price = self.market.get_stock(holding.ticker).value * holding.quantity
                result += f'{holding.ticker}({holding.quantity}) with a value of {stock_price}\n'
            await ctx.send(result)
            return
        else:
            if is_self:
                await ctx.send(f'You don\'t have any stock holdings yet. Try buying some stock!')
            else:
                await ctx.send(f'{user.name} doesn\'t have any stock holdings yet.')

    @stock.command(name='list')
    async def _list(self, ctx):
        """
        List the stocks on the market
        """
        result = ''
        for stock in self.market.stocks:
            result += f'{stock.ticker}({stock.available}) has a value of {stock.value} dbucks\n'
        await ctx.send(result)

    @stock.command(name='create')
    async def _create(self, ctx, ticker: str):
        """
        Create and add a new stock to the market
        """
        if len(self.market.stocks) + 1 > self.market.MAX_STOCKS:
            await ctx.send(f'Maximum of {self.market.MAX_STOCKS} hit')
            return
        user_id = ctx.author.id
        account = self.bank.get_account(user_id)
        if account is None:
            await ctx.send(f'Hmmm, looks like you don\'t have an account yet. You\'ll need one to make a stock')
            return
        stock = next(filter(lambda s: s.ticker == ticker, self.market.stocks), None)
        if stock is not None:
            await ctx.send(f'Stock with ticker {ticker} already exists!')
            return
        if len(ticker) > 8 or not (ticker.isupper() and ticker.isalpha()):
            await ctx.send(f'Please enter a valid ticker name (all uppercase letters and 8 or less characters)')
            return
        if account.value < STOCK_CREATION_PRICE:
            await ctx.send(f'You do not have enough dbucks to create a stock. Stock creation costs {STOCK_CREATION_PRICE} dbucks')
            return

        stock = Stock(ticker, STOCK_STARTING_AVAILABILITY, STOCK_STARTING_PRICE)
        self.market.stocks.append(stock)
        self.market.save_stocks()
        self.bank.make_payment(account.account_id, STOCK_CREATION_PRICE)
        await ctx.send(f'Stock {ticker} created!')

