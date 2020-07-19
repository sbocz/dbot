import os
import sys
import logging


from discord.ext import commands
from dotenv import load_dotenv

sys.path.append(os.pardir)
sys.path.append(os.path.join(os.pardir, os.pardir))

from src.clients.inspirobot_client import InspirobotClient
from src.clients.urban_dictionary_client import UrbanDictionaryClient
from src.cogs.stock_cog import StockCog
from src.commerce.bank import Bank
from src.cogs.dbucks_cog import DbucksCog
from src.cogs.generic_cog import GenericCog
from src.commerce.market import Market


# Load environment variables
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
COMMAND_PREFIX = os.getenv('COMMAND_PREFIX').split('|')
if os.getenv('COMMAND_WITH_SPACE'):
    for i, prefix in enumerate(COMMAND_PREFIX):
        COMMAND_PREFIX[i] = prefix + ' '
BRAIN_PATH = os.getenv('BRAIN_PATH')

# Set up logger
logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)
handler = logging.FileHandler(filename='logs/discord.log', encoding='utf-8')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

# Initialize bot
bot = commands.Bot(command_prefix=COMMAND_PREFIX, description='Discord bot tapped into Esbee\'s subconscious')

bank = Bank()
market = Market()
bot.add_cog(GenericCog(bot, InspirobotClient(), UrbanDictionaryClient()))
bot.add_cog(DbucksCog(bot, bank))
bot.add_cog(StockCog(bot, bank, market))
bot.run(TOKEN)
