import logging
import aiohttp

log = logging.getLogger('discord')
INSPIROBOT_GENERATE_URL = 'https://inspirobot.me/api?generate=true'


class InspirobotClient:
    """Client for interacting with inspirobot"""
    def __init__(self):
        self.generate_url = INSPIROBOT_GENERATE_URL

    @staticmethod
    async def fetch(session, url):
        """Performs a GET on a URL"""
        async with session.get(url) as response:
            return await response.text()

    async def generate_inspirational_message(self):
        """Gets an inspirational message from inspirobot"""
        async with aiohttp.ClientSession() as session:
            html = await self.fetch(session, self.generate_url)
            return html
