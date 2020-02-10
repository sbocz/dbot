import logging
from datetime import datetime

import discord
from discord.ext import commands, tasks

from src.utility import read_list_from_file, write_list_to_file

log = logging.getLogger('discord')
BANK_FILE = 'brain/bank.txt'


class DbucksCog(commands.Cog, name='dbucks'):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None
        self.accounts = self.load_accounts(BANK_FILE)

    @staticmethod
    def load_accounts(filename):
        account_list = read_list_from_file(filename)
        accounts = {}
        for account in account_list:
            parsed_account = account.split("|")
            accounts[parsed_account[0]] = {'value': int(parsed_account[1]), 'interest_date': datetime.fromtimestamp(int(float(parsed_account[2])))}
        return accounts

    def save_accounts(self):
        account_list = []
        for key in self.accounts.keys():
            value = self.accounts[key]['value']
            interest_date = self.accounts[key]['interest_date'].timestamp()
            account_list.append(f'{key}|{value}|{interest_date}')
        write_list_to_file(BANK_FILE, account_list)

    @tasks.loop(minutes=10.0)
    async def backup_brain(self):
        log.info("Backing up the Dbucks Cog")
        self.save_accounts()

    @tasks.loop(hours=6.0)
    async def pay_interest(self):
        log.info("Paying interest")
        for key in self.accounts.keys():
            # Check if it has been a day
            if (datetime.today() - self.accounts[key]['interest_date']).days >= 1:
                log.info(f'Paying interest to user: {key}')
                self.accounts[key]['value'] += 20
                self.accounts[key]['interest_date'] = datetime.today()
        self.save_accounts()

    @commands.Cog.listener()
    async def on_ready(self):
        self.backup_brain.start()
        self.pay_interest.start()

    @commands.group(name='bank')
    async def bank(self, ctx):
        """
        Interact with the bank
        """
        if ctx.invoked_subcommand is None:
            await ctx.send(f'bank "{ctx.subcommand_passed}" is not a command')

    @bank.command(name='help')
    async def _help(self, ctx):
        """
        HELP
        """
        await ctx.send_help(ctx.command.parent)

    @bank.command(name='openaccount')
    async def _openaccount(self, ctx):
        """
        Create an account
        """
        user_id = ctx.author.id

        if user_id in self.accounts:
            await ctx.send(f'You already have an account registered. Your balance is {self.accounts[user_id]["value"]} dbucks')
        else:
            # 10 dbucks per day in the guild
            days_in_guild = (datetime.today() - ctx.author.joined_at).days
            self.accounts[user_id] = {'value': days_in_guild * 10, 'interest_date': datetime.today()}
            self.save_accounts()
            await ctx.send(f"Thank you for registering your account {ctx.author.mention}! Your balance is {self.accounts[user_id]['value']} dbucks")

    @commands.command(name='balance')
    async def balance(self, ctx, member: discord.Member = None):
        """
        Display an account balance
        """
        if member is None:
            user_id = ctx.author.id
            if user_id in self.accounts:
                await ctx.send(
                    f'Hello {ctx.author.mention}, your balance is {self.accounts[user_id]["value"]} dbucks')
            else:
                await ctx.send(
                    f'Hmmm, looks like you don\'t have an account yet. Try the "bank openaccount" command.')
        else:
            user_id = member.id
            if user_id in self.accounts:
                await ctx.send(
                    f'{member.mention} has a balance of {self.accounts[user_id]["value"]} dbucks')
            else:
                await ctx.send(
                    f'Hmmm, looks like they don\'t have an account yet. Try the "bank openaccount" command.')

    @commands.command(name='tip')
    async def tip(self, ctx, member: discord.Member, value: int):
        """Tip another account"""
        user_id = ctx.author.id
        if value < 1:
            await ctx.send(
                f'Cannot tip less than 1 dbuck')
        if value > 10000:
            await ctx.send(
                f'That\'s too much man. Must tip 10,000 dbucks or fewer')
        if user_id not in self.accounts:
            await ctx.send(
                f'Hmmm, looks like you don\'t have an account yet. Try the "bank openaccount" command.')
            return
        if self.accounts[user_id]["value"] < value:
            await ctx.send(
                f'Your balance is {self.accounts[user_id]["value"]}, you\'ll need to save up more to tip that much!')
            return
        if member.id not in self.accounts:
            await ctx.send(
                f'Hmmm, looks like {member.mention} doesn\'t have an account yet. Try the "bank openaccount" command.')
            return
        self.accounts[user_id]["value"] -= value
        self.accounts[member.id]["value"] += value
        await ctx.send(
            f'{ctx.author.mention} tipped {member.mention} 𝔻 {value:,}')
        self.save_accounts()
