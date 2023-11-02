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

    async def __get(self, method: str) -> dict:
        async with aiohttp.ClientSession() as session:
            async with session.get(f'{self.url}{method}', headers=self.headers) as response:
                return await response.json()

    async def __post(self, method: str, data: dict = None) -> dict:
        async with aiohttp.ClientSession() as session:
            async with session.post(f'{self.url}{method}', json=data, headers=self.headers) as response:
                return await response.json()

    async def __patch(self, method: str, data: dict) -> dict:
        async with aiohttp.ClientSession() as session:
            async with session.patch(f'{self.url}{method}', json=data, headers=self.headers) as response:
                return await response.json()

    async def __delete(self, method: str) -> dict:
        async with aiohttp.ClientSession() as session:
            async with session.delete(f'{self.url}{method}', headers=self.headers) as response:
                return await response.json()

    async def get_database(self, db_id: str) -> dict:
        method = f'databases/{db_id}'
        return await self.__get(method)

    async def database_query(self, db_id: str) -> dict:
        method = f'databases/{db_id}/query'
        return await self.__post(method=method)

    async def insert_into_db(self, db_id: str) -> dict:
        method = 'pages'
        data = {
            'parent': {
                'type': 'database_id',
                'database_id': db_id
            },
            'properties': {
                'Name': {
                    'title': [
                        {
                            'text': {
                                'content': 'Ololotrololo'
                            }
                        }
                    ]
                },
                'Number': {
                    'number': 12541
                },
                'Text': {
                    'multi_select': [
                        {
                            'name': 'text2'
                        }
                    ]
                }
            }
        }
        return await self.__post(method=method, data=data)

    async def delete_block(self):
        method = 'blocks/c6e6b21a-afac-454b-8b14-0d845fd4cf05'
        return await self.__delete(method=method)

    async def create_table(self):
        """PAGE_ID"""
        method = 'blocks/0acf167a819e420da46425965e8de441/children'
        data = {
            'children': [
                {
                    'table': {
                        'table_width': 6,
                        'has_column_header': True,
                        'children': [
                            {
                                "table_row": {
                                    'cells': [
                                        [{'text': {'content': 'AUTOTEXT'}}],
                                        [{'text': {'content': 'AUTOTEXT'}}],
                                        [{'text': {'content': 'AUTOTEXT'}}],
                                        [{'text': {'content': 'AUTOTEXT'}}],
                                        [{'text': {'content': 'AUTOTEXT'}}],
                                        [{'text': {'content': 'AUTOTEXT'}}]
                                    ]
                                }
                            }
                        ]
                    }
                }
            ]
        }
        response = await self.__patch(method=method, data=data)
        print(response)

    async def update_table_row(self):
        method = 'blocks/c6e6b21a-afac-454b-8b14-0d845fd4cf05/children'
        data = {
            'children': [
                {
                    "table_row": {
                        'cells': [
                            [{'text': {'content': 'AUTOTEXT'}}],
                            [{'text': {'content': 'AUTOTEXT'}}],
                            [{'text': {'content': 'AUTOTEXT'}}],
                            [{'text': {'content': 'AUTOTEXT'}}]
                        ]
                    }
                }
            ]
        }
        response = await self.__patch(method=method, data=data)
        print(response)


async def main():
    db_id = 'a98b1f4047b84889a6e340fe482f4c7b'
    res = await Notion().get_database(db_id)
    # res = await Notion().database_query(db_id)
    # res = await Notion().insert_into_db(db_id)
    pprint(res)

asyncio.run(main())
