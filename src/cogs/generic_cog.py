import logging
import os
import random
import traceback

from discord import ActivityType
from ratelimit import limits
import discord
from discord.ext import commands, tasks
from discord.ext.commands import BucketType

from src.status import Status
from src.utility import read_json_from_file, write_json_to_file


# File constants
YELL_FILE = os.path.join(os.getenv('BRAIN_PATH'), 'yell.json')
YELL_BLACKLIST_FILE = os.path.join(os.getenv('BRAIN_PATH'), 'yell_blacklist.json')
FORTUNES = os.path.join(os.getenv('BRAIN_PATH'), 'fortunes.json')
STATUSES_FILE = os.path.join(os.getenv('BRAIN_PATH'), 'statuses.json')

rate = 10
period = 120
log = logging.getLogger('discord')


class GenericCog(commands.Cog, name='Generic'):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None
        self.yell_list = read_json_from_file(YELL_FILE)
        self.yell_blacklist = read_json_from_file(YELL_BLACKLIST_FILE)
        self.fortunes = read_json_from_file(FORTUNES)
        self.statuses = self.build_statuses(STATUSES_FILE)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        channel = member.guild.system_channel
        if channel is not None:
            await channel.send('Welcome {0.mention}.'.format(member))

    @commands.Cog.listener()
    async def on_message(self, message):
        log.debug('Firing on_message event')
        if message.author.id == self.bot.user.id:
            return
        if len(str(message.content)) > 2 and str(message.content).isupper():
            await self.yell(message)

    @limits(calls=rate, period=period)
    async def yell(self, message):
        log.info(f'Firing \'yell\' command for message \'{message.content}\'')
        choice = random.choice(self.yell_list)

        if not any(word in message.content for word in self.yell_blacklist):
            log.info("Added '{0}' to capsList".format(message.content))
            self.yell_list.append(message.content)

        await message.channel.send(choice)
        return

    @commands.command()
    @commands.cooldown(rate, period, BucketType.user)
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
    @commands.cooldown(rate, period, BucketType.user)
    async def choose(self, ctx, *choices: str):
        """Chooses between multiple choices."""
        await ctx.send(random.choice(choices))

    @commands.command(description='Poke me')
    @commands.cooldown(rate, period, BucketType.user)
    async def ping(self, ctx):
        await ctx.send('PONG')

    @commands.command()
    @commands.cooldown(rate, period, BucketType.user)
    async def joined(self, ctx, member: discord.Member):
        """Says when a member joined."""
        await ctx.send(
            f"{member.name} joined on {member.joined_at.strftime('%Y-%m-%d')}")

    @commands.command(name='8ball')
    @commands.cooldown(rate, period, BucketType.user)
    async def eight_ball(self, ctx):
        """Fortunes from beyond."""
        choice = random.choice(self.fortunes)
        await ctx.send(choice)

    @staticmethod
    def build_statuses(filename):
        # Format of the file is "PLAYING|Game", etc.
        json_list = read_json_from_file(filename)
        statuses = []
        for d in json_list:
            status = Status.from_dict(d)
            statuses.append(status)
        return statuses

    @tasks.loop(minutes=20.0)
    async def change_status(self):
        choice: Status = random.choice(self.statuses)
        log.info(f'Updating status message: {choice.activity}')
        await self.bot.change_presence(activity=choice.activity)

    @tasks.loop(minutes=60.0)
    async def backup_brain(self):
        log.info("Backing up the Generic Cog")
        write_json_to_file(YELL_FILE, list(set(self.yell_list)))
        write_json_to_file(YELL_BLACKLIST_FILE, list(set(self.yell_blacklist)))
        write_json_to_file(FORTUNES, list(set(self.fortunes)))

    @commands.Cog.listener()
    async def on_ready(self):
        log.info('Firing on_ready event')
        self.change_status.start()
        self.backup_brain.start()

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        # this event is called every time an exception occurs during a command's processing.
        # this can be caused by parsing errors (e.g. invalid quotes or a converter raising the exception),
        # a command being on cooldown, disabled, not found or a general invoke error.
        #
        # ctx   = the command's context
        # error = the exception raised

        # this checks if the command has a local error handler (see above),
        # if so skip all the below handling.
        if hasattr(ctx.command, "on_error"):
            return

        if isinstance(error, commands.CommandInvokeError):
            error = error.original

        # do nothing since we don't really care in this case
        if isinstance(error, commands.CommandNotFound):
            log.warning(error.args[0])
            return

        # as the name says, this catches all errors derived from user input.
        elif isinstance(error, commands.UserInputError):
            # this is fine for most use cases since it replies with a friendly error message.
            await ctx.send(error)

        # the command is on cooldown
        elif isinstance(error, commands.CommandOnCooldown):
            # we can easily access the exception and context's attributes to give a more helpful error message.
            msg = "The \"{0}\" command is on cooldown, wait {1:.2f} seconds.".format(ctx.command.name,
                                                                                     error.retry_after)
            await ctx.send(msg)

        # here you can handle all other types of exceptions.

        else:
            await ctx.send("An unexpected error has occurred and my developer has been notified, sorry.")
            # make sure to always print the exception's traceback at the end of the event, else it will be "eaten".

            # Note: it's impossible to use traceback.print_exc() or traceback.format_exc() due to
            # how event dispatching messes with the exception context.

            traceback.print_exception(type(error), error, error.__traceback__)
