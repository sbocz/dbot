import os
import sys
sys.path.append(os.pardir)
sys.path.append(os.path.join(os.pardir, os.pardir))

import logging

from discord.ext import commands
from dotenv import load_dotenv

from src.clients.inspirobot_client import InspirobotClient
from src.clients.urban_dictionary_client import UrbanDictionaryClient
from src.cogs.stock_cog import StockCog
from src.commerce.bank import Bank
from src.cogs.dbucks_cog import DbucksCog
from src.cogs.generic_cog import GenericCog
from src.commerce.market import Market

command_prefix = '!'
token = ''
logger = logging.getLogger('discord')
rate = 10
period = 120
brain_path = ''


def configure_logging(logging_level, filename):
    logger.setLevel(logging_level)
    handler = logging.FileHandler(filename=filename, encoding='utf-8')
    handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
    logger.addHandler(handler)


def initialize_configuration():
    load_dotenv()
    global token
    global command_prefix
    global brain_path
    token = os.getenv('DISCORD_TOKEN')
    command_prefix = os.getenv('COMMAND_PREFIX').split('|')
    if os.getenv('COMMAND_WITH_SPACE'):
        for i, prefix in enumerate(command_prefix):
            command_prefix[i] = prefix + ' '
    brain_path = os.getenv('BRAIN_PATH')


# Load environment variables
initialize_configuration()

# Set up logger
configure_logging(logging.INFO, 'logs/discord.log')

# Initialize bot
bot = commands.Bot(command_prefix=command_prefix, description='Discord bot tapped into Esbee\'s subconscious')

bank = Bank()
market = Market()
bot.add_cog(GenericCog(bot, InspirobotClient(), UrbanDictionaryClient()))
bot.add_cog(DbucksCog(bot, bank))
bot.add_cog(StockCog(bot, bank, market))
bot.run(token)
