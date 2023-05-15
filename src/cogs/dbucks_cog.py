import logging
from datetime import datetime
from operator import itemgetter

import discord
from discord.ext import commands, tasks

from commerce.bank import Bank

log = logging.getLogger("discord")
CURRENCY = "𝔻"


class DbucksCog(commands.Cog, name="dbucks"):
    """Commands for interacting with currency"""

    def __init__(self, bot: commands.Bot, bank: Bank):
        self.bot = bot
        self._last_member = None
        self.bank = bank

    @tasks.loop(hours=6.0)
    async def pay_interest(self):
        """Triggers the bank to pay interest on a timer"""
        log.info("Paying interest")
        self.bank.pay_interest()

    @commands.Cog.listener()
    async def on_ready(self):
        """Starts all currency related tasks"""
        self.pay_interest.start()

    @commands.group(name="bank")
    async def bank_command(self, ctx):
        """
        Interact with the bank
        """
        if ctx.invoked_subcommand is None:
            await ctx.send(f'bank "{ctx.subcommand_passed}" is not a command')

    @bank_command.command(name="help")
    async def _help(self, ctx):
        """
        HELP
        """
        await ctx.send_help(ctx.command.parent)

    @bank_command.command(name="openaccount")
    async def _openaccount(self, ctx):
        """
        Create an account
        """
        user_id = ctx.author.id
        user_account = self.bank.get_account(user_id)
        if user_account is not None:
            await ctx.send(
                f"You already have an account registered. Your balance is {user_account.value} dbucks"
            )
        else:
            # 10 dbucks per day in the guild
            days_in_guild = (datetime.today() - ctx.author.joined_at).days
            user_account = self.bank.create_account(user_id, days_in_guild * 10)
            await ctx.send(
                f"Thank you for registering your account {ctx.author.mention}! Your balance is {user_account.value} dbucks"
            )

    @bank_command.command(name="accounts")
    async def _accounts(self, ctx):
        """
        List bank accounts and their balances
        """
        result = ""
        account_tuples = []
        for account in self.bank.get_accounts():
            log.info(f"Listing account for ID {account.account_id}")
            user: discord.User = self.bot.get_user(account.account_id)
            log.info(f"User retrieved {user}")
            # If an account is removed from Discord the account shows as None
            if user != None:
                account_tuples.append((user.name, account.value))
        account_tuples.sort(key=itemgetter(1))
        account_tuples.reverse()
        for account in account_tuples:
            result += f"{account[0]} has a balance of {account[1]}{CURRENCY}\n"
        await ctx.send(result)

    @commands.command(name="balance")
    async def balance(self, ctx, member: discord.Member = None):
        """
        Display an account balance
        """
        if member is None:
            user_id = ctx.author.id
            account = self.bank.get_account(user_id)
            if account is not None:
                await ctx.send(
                    f"Hello {ctx.author.mention}, your balance is {account.value} dbucks"
                )
            else:
                await ctx.send(
                    f'Hmmm, looks like you don\'t have an account yet. Try the "bank openaccount" command.'
                )
        else:
            user_id = member.id
            account = self.bank.get_account(user_id)
            if account is not None:
                await ctx.send(
                    f"{member.mention} has a balance of {account.value} dbucks"
                )
            else:
                await ctx.send(
                    f'Hmmm, looks like they don\'t have an account yet. Try the "bank openaccount" command.'
                )

    @commands.command(name="tip")
    async def tip(self, ctx, member: discord.Member, value: int):
        """Tip another account"""
        user_id = ctx.author.id
        if value < 1:
            await ctx.send(f"Cannot tip less than 1 dbuck")
            return
        if value > 10000:
            await ctx.send(f"That's too much man. Must tip 10,000 dbucks or fewer")
            return
        payer = self.bank.get_account(user_id)
        payee = self.bank.get_account(member.id)
        if payer is None:
            await ctx.send(
                f'Hmmm, looks like you don\'t have an account yet. Try the "bank openaccount" command.'
            )
            return
        if payer.value < value:
            await ctx.send(
                f"Your balance is {payer.value}, you'll need to save up more to tip that much!"
            )
            return
        if payee is None:
            await ctx.send(
                f'Hmmm, looks like {member.mention} doesn\'t have an account yet. Try the "bank openaccount" command.'
            )
            return
        self.bank.make_payment(payer.account_id, value, payee.account_id)
        await ctx.send(
            f"{ctx.author.mention} tipped {member.mention} {value:,}{CURRENCY}"
        )
