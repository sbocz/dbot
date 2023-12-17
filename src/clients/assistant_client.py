import json
import logging
import aiohttp

log = logging.getLogger("discord")
ASSISTANT_URL = "http://127.0.0.1:5000/message"


class AssistantClient:
    """HTTP Client that interacts with AI assistant"""

    def __init__(self):
        self.api_url = ASSISTANT_URL

    @staticmethod
    async def fetch_json(session: aiohttp.ClientSession, url: str, data: dict):
        """Performs a POST on an endpoint with some data and retuns the resulting JSON body"""
        json_data = json.dumps(data)
        async with session.post(
            url=url, data=json_data, headers={"Content-Type": "application/json"}
        ) as response:
            return await response.json()

    async def chat(self, thread_id: str, message: str) -> str:
        """Sends a change to the assistant and gets the response"""
        async with aiohttp.ClientSession() as session:
            data = {"thread_id": str(thread_id), "message": message}
            log.info(f"Calling assistant at URL '{self.api_url}' with data '{data}'.")
            result_json = await self.fetch_json(session, self.api_url, data)
            if "response" in result_json:
                log.info(f"AI assistant response: '{result_json}'.")
                return result_json["response"]
            else:
                log.error(
                    f"Failed to communicate with ai assistant. Resulting JSON: '{result_json}'"
                )
                return "Failed to get response from chat assistant. My developer has been notified, sorry."
