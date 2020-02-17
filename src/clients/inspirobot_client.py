import aiohttp
import logging

log = logging.getLogger('discord')
INSPIROBOT_GENERATE_URL = 'https://inspirobot.me/api?generate=true'


class InspirobotClient:
    def __init__(self):
        self.generate_url = INSPIROBOT_GENERATE_URL

    @staticmethod
    async def fetch(session, url):
        async with session.get(url) as response:
            return await response.text()

    async def generate_inspirational_message(self):
        async with aiohttp.ClientSession() as session:
            html = await self.fetch(session, self.generate_url)
            return html
