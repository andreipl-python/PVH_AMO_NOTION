import asyncio
from pprint import pprint

import aiohttp

class Notion:
    def __init__(self):
        self.url = 'https://api.notion.com/v1/'
        self.headers = {
            "Authorization": "Bearer " + 'secret_5TAmPtQabH5LRFfTkNdDaE1m2MA4us1QwQwGk6O1rKo',
            "Notion-Version": "2022-06-28",
            "Content-Type": "application/json"
        }

    async def get(self, method: str) -> dict:
        async with aiohttp.ClientSession() as session:
            async with session.get(f'{self.url}{method}', headers=self.headers) as response:
                return await response.json()

    async def post(self, method: str, data: dict) -> dict:
        async with aiohttp.ClientSession() as session:
            async with session.post(f'{self.url}{method}', json=data, headers=self.headers) as response:
                return await response.json()

    async def get_users(self):
        method = 'pages/0acf167a819e420da46425965e8de441'
        return await self.get(method)



async def main():
    users = await Notion().get_users()
    pprint(users)

asyncio.run(main())