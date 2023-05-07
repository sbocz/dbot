import os
import sys
import logging
import discord
import asyncio

from discord.ext import commands
from dotenv import load_dotenv
env_path = '../config/.env'
# Set env vars before other modules are initializied which use env vars to locate data files
load_dotenv(dotenv_path=env_path)

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
TOKEN = os.getenv('DISCORD_TOKEN')
COMMAND_PREFIX = os.getenv('COMMAND_PREFIX').split('|')
if os.getenv('COMMAND_WITH_SPACE'):
    for i, prefix in enumerate(COMMAND_PREFIX):
        COMMAND_PREFIX[i] = prefix + ' '
BRAIN_PATH = os.getenv('BRAIN_PATH')

# Set up logger
logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)
if not os.path.exists('logs'):
    os.makedirs('logs')
handler = logging.FileHandler(filename='logs/discord.log', encoding='utf-8')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

# Initialize bot
intents = discord.Intents.all()
bot = commands.Bot(command_prefix=COMMAND_PREFIX, intents=intents, description='Discord bot tapped into Esbee\'s subconscious')

bank = Bank()
market = Market()


async def main():
    async with bot:
        await bot.add_cog(GenericCog(bot, InspirobotClient(), UrbanDictionaryClient()))
        await bot.add_cog(DbucksCog(bot, bank))
        await bot.add_cog(StockCog(bot, bank, market))
        await bot.start(TOKEN)

asyncio.run(main())
