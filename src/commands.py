import random

import discord
from discord.ext import commands

<<<<<<< HEAD:src/commands.py
from src.utility import read_list_from_file
=======
from utility import read_list_from_file
>>>>>>> 2fb180235bb967d3b26937fa692fa3aa7464312f:commands.py

yell_list = read_list_from_file('brain/yell.txt')
yell_blacklist = read_list_from_file('brain/yell_blacklist.txt')
fortunes = read_list_from_file('brain/fortunes.txt')


class Dbot(commands.Cog):
    logger = None

    def __init__(self, bot, logger):
        self.bot = bot
        self._last_member = None
        self.logger = logger

    @commands.Cog.listener()
    async def on_member_join(self, member):
        channel = member.guild.system_channel
        if channel is not None:
            await channel.send('Welcome {0.mention}.'.format(member))

    @commands.Cog.listener()
    async def on_message(self, message):
        self.logger.debug('Firing on_message event')
        if message.author.id == self.bot.user.id:
            return

        if len(str(message.content)) > 2 and str(message.content).isupper():
            self.logger.info(f'Firing \'yell\' command for message \'{message.content}\'')
            choice = random.choice(yell_list)

            if not any(word in message.content for word in yell_blacklist):
                self.logger.info("Added '{0}' to capsList".format(message.content))
                yell_list.append(message.content)

            await message.channel.send(choice)
            return

    @commands.command()
    async def add(self, ctx, left: int, right: int):
        """Adds two numbers together."""
        await ctx.send(left + right)

    @commands.command()
    async def roll(self, ctx, dice: str):
        """Rolls a dice in NdN format."""
        try:
            rolls, limit = map(int, dice.split('d'))
        except Exception:
            await ctx.send('Format has to be in NdN!')
            return

        results = []
        for r in range(rolls):
            results.append(random.randint(1, limit))

        result = ', '.join(str(r) for r in results) + ' (' + str(sum(results)) + ')'
        await ctx.send(result)

    @commands.command(description='For when you wanna settle the score some other way')
    async def choose(self, ctx, *choices: str):
        """Chooses between multiple choices."""
        await ctx.send(random.choice(choices))

    @commands.command(description='Poke me')
    async def ping(self, ctx):
        await ctx.send('PONG')

    @commands.command()
    async def repeat(self, ctx, times: int, content='repeating...'):
        """Repeats a message multiple times."""
        for i in range(times):
            await ctx.send(content)

    @commands.command()
    async def joined(self, ctx, member: discord.Member):
        """Says when a member joined."""
        await ctx.send(
            f"{member.name} joined on {member.joined_at.year}-{member.joined_at.month}-{member.joined_at.day}")

    @commands.command(name='8ball')
    async def eight_ball(self, ctx):
        """Fortunes from beyond."""
        choice = random.choice(fortunes)
        await ctx.send(choice)
