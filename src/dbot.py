import asyncio
import logging
import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

from clients.inspirobot_client import InspirobotClient
from clients.urban_dictionary_client import UrbanDictionaryClient
from cogs.dbucks_cog import DbucksCog
from cogs.generic_cog import GenericCog
from cogs.stock_cog import StockCog
from commerce.bank import Bank
from commerce.market import Market

# Load environment variables
env_path = '../config/.env'
load_dotenv(dotenv_path=env_path)
token = os.getenv('DISCORD_TOKEN')
command_prefix = os.getenv('COMMAND_PREFIX').split('|')
if os.getenv('COMMAND_WITH_SPACE'):
    for i, prefix in enumerate(command_prefix):
        command_prefix[i] = prefix + ' '
brain_path = os.getenv('BRAIN_PATH')

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
bot = commands.Bot(command_prefix=command_prefix, intents=intents, description='Discord bot tapped into Esbee\'s subconscious')

bank = Bank(brain_path)
market = Market(brain_path)


async def main():
    async with bot:
        await bot.add_cog(GenericCog(bot, InspirobotClient(), UrbanDictionaryClient(), brain_path))
        await bot.add_cog(DbucksCog(bot, bank))
        await bot.add_cog(StockCog(bot, bank, market))
        await bot.start(token)

asyncio.run(main())
