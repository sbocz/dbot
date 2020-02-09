import random
import logging
import os

import discord
from discord import ActivityType
from discord.ext import commands, tasks
from dotenv import load_dotenv


capsList = [

]

blackList = [
]


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
            choice = random.choice(capsList)

            if not any(word in message.content for word in blackList):
                self.logger.info("Added '{0}' to capsList".format(message.content))
                capsList.append(message.content)

            await message.channel.send(choice)
            return

        # await self.bot.process_commands(message)

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
        await ctx.send('{0.name} joined on {0.joined_at.year}-{0.joined_at.month}-{0.joined_at.day}'.format(member))

    @commands.command(name='8ball')
    async def eight_ball(self, ctx):
        """Fortunes from beyond."""
        fortunes = [
            'Concentrate and ask again.',
            'It is certain.',
            'It is decidedly so.',
            'Without a doubt.',
            'Yes - definitely.',
            'You may rely on it.',
            'As I see it, yes.',
            'Most likely.',
            'Outlook good.',
            'Yes.',
            'Signs point to yes.',
            'Reply hazy, try again.',
            'Ask again later.',
            'Better not tell you now.',
            'Cannot predict now.',
            'Don\'t count on it.',
            'My reply is no.',
            'My sources say no.',
            'Outlook not so good.',
            'Very doubtful.',
            'Bruh...',
            'It\'s entirely possible.',
            'Yas Queen.',
            'It is known.',
            'Only Allah knows.',
            'Not today.',
            ':thumbsdown:',
            ':potato:',
        ]
        choice = random.choice(fortunes)
        await ctx.send(choice)
