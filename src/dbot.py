import logging
import os
import discord
import random

from discord.ext import commands, tasks
from discord import ActivityType
from dotenv import load_dotenv

from src.generic_cog import GenericCog
from src.utility import read_list_from_file
from utility import read_list_from_file

command_prefix = '!'
token = ''
logger = logging.getLogger('discord')
rate = 10
period = 120


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

bot.add_cog(GenericCog(bot, logger))
bot.run(token)
