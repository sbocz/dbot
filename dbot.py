import logging
import os
import discord
import random

from discord.ext import commands, tasks
from discord import ActivityType
from dotenv import load_dotenv
from commands import Dbot
from utility import read_list_from_file

command_prefix = '!'
token = ''
logger = logging.getLogger('discord')
PLAYING_ACTIVITY = 'PLAYING'
LISTENING_ACTIVITY = 'LISTENING'
WATCHING_ACTIVITY = 'WATCHING'
STREAMING_ACTIVITY = 'STREAMING'


def configure_logging(logging_level, filename):
    logger.setLevel(logging_level)
    handler = logging.FileHandler(filename=filename, encoding='utf-8', mode='w')
    handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
    logger.addHandler(handler)


def initialize_configuration():
    load_dotenv()
    global token
    global command_prefix
    token = os.getenv('DISCORD_TOKEN')
    command_prefix = os.getenv('COMMAND_PREFIX').split('|')
    if os.getenv('COMMAND_WITH_SPACE'):
        for i, prefix in enumerate(command_prefix):
            command_prefix[i] = prefix + ' '


# Load environment variables
initialize_configuration()

# Set up logger
configure_logging(logging.INFO, 'logs/discord.log')

# Initialize bot
bot = commands.Bot(command_prefix=command_prefix, description='Discord bot tapped into Esbee\'s subconscious')


def build_statuses():
    # Format of the file is "PLAYING|Game", etc.
    status_list = read_list_from_file('brain/statuses.txt')
    statuses = []
    for item_parsed in status_list:
        pair = item_parsed.split('|')
        switcher = {
            WATCHING_ACTIVITY: ActivityType.watching,
            LISTENING_ACTIVITY: ActivityType.listening,
            PLAYING_ACTIVITY: ActivityType.playing,
            STREAMING_ACTIVITY: ActivityType.streaming
        }

        # Build status tuple eg. ('Game', ActivityType.playing)
        status = (pair[1], switcher.get(pair[0], ActivityType.playing))
        statuses.append(status)
    return statuses


@tasks.loop(minutes=20.0)
async def change_status():
    statuses = build_statuses()
    choice = random.choice(statuses)
    activity = discord.Activity(name=choice[0], type=choice[1])
    logger.info('Updating status message: {0}'.format(activity))
    await bot.change_presence(activity=activity)


@bot.event
async def on_ready():
    logger.info('Firing on_ready event')
    change_status.start()

bot.add_cog(Dbot(bot, logger))
bot.run(token)
