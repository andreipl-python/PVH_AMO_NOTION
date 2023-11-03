import asyncio
from pprint import pprint

import aiohttp

from models import AmoCustomField
from sql import SQLiteDB


class Notion:
    def __init__(self):
        self.url = 'https://api.notion.com/v1/'
        self.db_id = 'a98b1f4047b84889a6e340fe482f4c7b'
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

    async def get_database(self) -> dict:
        method = f'databases/{self.db_id}'
        return await self.__get(method)

    async def database_query(self, db_id: str) -> dict:
        method = f'databases/{db_id}/query'
        return await self.__post(method=method)

    async def insert_into_db(self, field: AmoCustomField) -> dict:
        method = 'pages'

        properties = {
            'group_name': {
                'select': {
                    'name': field.group_name if field.group_name else 'Without group'
                }
            },
            'id': {
                'number': field.field_id
            },
            'sort': {
                'number': field.sort
            },
            'Название': {
                'title': [
                    {
                        'text': {
                            'content': field.name
                        }
                    }
                ]
            },
            'Наличие в аккаунте': {
                'select': {
                    'name': 'Присутствует' if field.is_deleted == 0 else 'Удалено'
                }
            },
            'Сущность': {
                'select': {
                    'name': field.entity
                }
            },
            'Тип поля': {
                'select': {
                    'name': field.field_type
                }
            }
        }

        data = {
            'parent': {
                'type': 'database_id',
                'database_id': self.db_id
            },
            'properties': properties
        }
        result = await self.__post(method=method, data=data)
        await SQLiteDB().update_field_data(field_id=field.field_id, set_values={'db_page_id': result.get('id')})
        return result

    async def delete_block(self, block_id: str):
        method = f'blocks/{block_id}'
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


async def main():
    # res = await Notion().get_database()
    # res = await Notion().database_query(db_id)
    test = AmoCustomField(name='Потенциал возврата', field_id=1005245, entity='leads', field_type='select', enums=None,
                          sort=639, required_statuses='3351007,143', group_name='leads_28471678882706', is_deleted=0,
                          db_page_id=None, enum_page_id=None, required_statuses_page_id=None)
    res = await Notion().insert_into_db(test)
    pprint(res)
#
#
asyncio.run(main())
