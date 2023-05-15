import logging
import os
import random
import traceback

from ratelimit import limits
import discord
from discord.ext import commands, tasks
from discord.ext.commands import BucketType

from clients.inspirobot_client import InspirobotClient
from clients.urban_dictionary_client import UrbanDictionaryClient
from status import Status
from utility import read_json_from_file, write_json_to_file

# File constants
YELL_FILE = 'yell.json'
YELL_BLACKLIST_FILE = 'yell_blacklist.json'
FORTUNES = 'fortunes.json'
STATUSES_FILE = 'statuses.json'

RATE = 10
PERIOD = 120
log = logging.getLogger('discord')


class GenericCog(commands.Cog, name='Generic'):
    """Generic and miscellaneous commands"""
    def __init__(self, bot, inspirobot: InspirobotClient, urban_dictionary: UrbanDictionaryClient, brain_path: str):
        self.urban_dictionary = urban_dictionary
        self.inspirobot = inspirobot
        self.bot = bot
        self._last_member = None
        self.yell_list = read_json_from_file(os.path.join(brain_path, YELL_FILE))
        self.yell_blacklist = read_json_from_file(os.path.join(brain_path, YELL_BLACKLIST_FILE))
        self.fortunes = read_json_from_file(os.path.join(brain_path, FORTUNES))
        self.statuses = self.build_statuses(os.path.join(brain_path, STATUSES_FILE))

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Welcome's a new member to a guild"""
        channel = member.guild.system_channel
        if channel is not None:
            await channel.send('Welcome {0.mention}.'.format(member))

    @commands.Cog.listener()
    async def on_message(self, message):
        """Listens to all messages that do not trigger another command"""
        log.debug('Firing on_message event')
        if message.author.id == self.bot.user.id:
            return
        if len(str(message.content)) > 2 and str(message.content).isupper():
            await self.yell(message)

    @limits(calls=RATE, period=PERIOD)
    async def yell(self, message):
        """Saves the provided message to the yell list and replies with a random yell"""
        log.info(f'Firing \'yell\' command for message \'{message.content}\'')

        if not any(word in message.content for word in self.yell_blacklist):
            log.info(f"Added 'message.content' to capsList")
            self.yell_list.append(message.content)
            choice = random.choice(self.yell_list)
            await message.channel.send(choice)
        else:
            await message.channel.send("My mother taught me not to say things like that!")
        return

    @commands.command()
    @commands.cooldown(RATE, PERIOD, BucketType.user)
    async def roll(self, ctx, dice: str):
        """Rolls a dice in NdN format."""
        try:
            rolls, limit = map(int, dice.split('d'))
        except ValueError:
            await ctx.send('Format has to be in NdN!')
            return

        results = []
        for _ in range(rolls):
            results.append(random.randint(1, limit))

        result = ', '.join(str(roll) for roll in results) + ' (' + str(sum(results)) + ')'
        await ctx.send(result)

    @commands.command(description='For when you wanna settle the score some other way')
    @commands.cooldown(RATE, PERIOD, BucketType.user)
    async def choose(self, ctx, *choices: str):
        """Chooses between multiple choices."""
        await ctx.send(random.choice(choices))

    @commands.command(description='Poke me')
    @commands.cooldown(RATE, PERIOD, BucketType.user)
    async def ping(self, ctx):
        """Pokes dbot to see if she's awake."""
        await ctx.send('PONG')

    @commands.command()
    @commands.cooldown(RATE, PERIOD, BucketType.user)
    async def joined(self, ctx, member: discord.Member):
        """Says when a member joined."""
        await ctx.send(
            f"{member.name} joined on {member.joined_at.strftime('%Y-%m-%d')}")

    @commands.command(name='8ball')
    @commands.cooldown(RATE, PERIOD, BucketType.user)
    async def eight_ball(self, ctx):
        """Fortunes from beyond."""
        choice = random.choice(self.fortunes)
        await ctx.send(choice)

    @commands.command(name='inspire')
    @commands.cooldown(5, 120, BucketType.guild)
    async def inspire(self, ctx):
        """For when you need a pick-me-up."""
        url = await self.inspirobot.generate_inspirational_message()
        await ctx.send(url)

    @commands.command(name='define')
    @commands.cooldown(10, 60 * 5, BucketType.guild)
    async def define(self, ctx, term_to_define: str, number_to_list: int = 1):
        """Define a term."""
        definition_list = await self.urban_dictionary.define(term_to_define)
        for definition in definition_list[:number_to_list]:
            message = \
                f'''=====
_{definition.word}_ \n
{definition.definition} \n
>>> {definition.example} \n
'''
            await ctx.send(message)

    @staticmethod
    def build_statuses(filename):
        """Constructs and returns a list of Discord statuses from a JSON file"""
        # Format of the file is "PLAYING|Game", etc.
        json_list = read_json_from_file(filename)
        statuses = []
        for dictionary in json_list:
            status = Status.from_dict(dictionary)
            statuses.append(status)
        return statuses

    @tasks.loop(minutes=20.0)
    async def change_status(self):
        """Changes dbot's status on a timer"""
        choice: Status = random.choice(self.statuses)
        log.info(f'Updating status message: {choice.activity}')
        await self.bot.change_presence(activity=choice.activity)

    @tasks.loop(minutes=60.0)
    async def backup_brain(self):
        """Backs up in-memory maps to JSON files"""
        log.info("Backing up the Generic Cog")
        write_json_to_file(YELL_FILE, list(set(self.yell_list)))
        write_json_to_file(YELL_BLACKLIST_FILE, list(set(self.yell_blacklist)))
        write_json_to_file(FORTUNES, list(set(self.fortunes)))

    @commands.Cog.listener()
    async def on_ready(self):
        """Starts the generic recurring tasks"""
        log.info('Firing on_ready event')
        self.change_status.start()
        self.backup_brain.start()

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """
        This event is called every time an exception occurs during a command's processing.
        This can be caused by parsing errors (e.g. invalid quotes or a converter raising the exception),
        a command being on cooldown, disabled, not found or a general invoke error.

        ctx   = the command's context
        error = the exception raised
        """

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
