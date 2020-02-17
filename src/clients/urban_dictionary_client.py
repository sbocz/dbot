import asyncio
import json
import urllib.parse

import aiohttp
import logging

from src.clients.models.definition import Definition

log = logging.getLogger('discord')
URBAN_DICTIONARY_API_URL = 'http://api.urbandictionary.com/v0/define'


class UrbanDictionaryClient:
    def __init__(self):
        self.api_url = URBAN_DICTIONARY_API_URL

    @staticmethod
    async def fetch_json(session, url):
        async with session.get(url) as response:
            return await response.json()

    async def define(self, term_to_define: str):
        async with aiohttp.ClientSession() as session:
            url = self.api_url + '?term=' + urllib.parse.quote_plus(term_to_define)
            result_json = await self.fetch_json(session, url)
            definitions = []
            for d in result_json['list']:
                definitions.append(Definition.from_dict(d))
            return definitions
