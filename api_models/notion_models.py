import aiohttp

from config_reader import config
from object_models import AmoCustomField
from sql import SQLiteDB


class Notion:
    def __init__(self):
        self.url = 'https://api.notion.com/v1/'
        self.db_id = config.db_id.get_secret_value()
        self.enum_db_id = config.enum_db_id.get_secret_value()
        self.headers = {
            "Authorization": "Bearer " + config.secret.get_secret_value(),
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

    async def get_database(self) -> dict:
        method = f'databases/{self.db_id}'
        return await self.__get(method)

    async def database_query(self) -> dict:
        method = f'databases/{self.db_id}/query'
        return await self.__post(method=method)

    async def insert_into_db(self, field: AmoCustomField) -> dict:
        method = 'pages'

        enums_property = []
        if field.enums:
            for enum_id in field.enums.split(':'):
                enum_data = await SQLiteDB().get_enum_data(int(enum_id))
                enums_property.append({'id': enum_data[0][3]})

        group_name = 'Without group'
        if field.group_id:
            group_data = await SQLiteDB().get_group_data(field.group_id)
            group_name = group_data[0][2]

        properties = {
            'group_name': {
                'select': {
                    'name': group_name
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
            },
            'Значение поля (enums)': {
                'relation': enums_property
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

    async def update_db_page(self, field: AmoCustomField) -> dict:
        method = f'pages/{field.db_page_id}'

        enums_property = []
        if field.enums:
            for enum_id in field.enums.split(':'):
                enum_data = await SQLiteDB().get_enum_data(int(enum_id))
                enums_property.append({'id': enum_data[0][3]})

        group_name = 'Without group'
        if field.group_id:
            group_data = await SQLiteDB().get_group_data(field.group_id)
            group_name = group_data[0][2]

        properties = {
            'group_name': {
                'select': {
                    'name': group_name
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
            },
            'Значение поля (enums)': {
                'relation': enums_property
            }
        }

        data = {
            'parent': {
                'type': 'database_id',
                'database_id': self.db_id
            },
            'properties': properties
        }
        result = await self.__patch(method=method, data=data)
        return result

    async def insert_into_enum_db(self, enum_id: int, value: str) -> dict:
        method = 'pages'

        properties = {
            'id': {
                'number': enum_id
            },
            'Value': {
                'title': [
                    {
                        'text': {
                            'content': value
                        }
                    }
                ]
            },
        }

        data = {
            'parent': {
                'type': 'database_id',
                'database_id': self.enum_db_id
            },
            'properties': properties
        }
        result = await self.__post(method=method, data=data)
        await SQLiteDB().update_enum_data(enum_id=enum_id, set_values={'db_page_id': result.get('id')})
        return result

    async def update_enum_page(self, enum_db_page_id: str, value: str) -> dict:
        method = f'pages/{enum_db_page_id}'

        properties = {
            'Value': {
                'title': [
                    {
                        'text': {
                            'content': value
                        }
                    }
                ]
            },
        }

        data = {
            'parent': {
                'type': 'database_id',
                'database_id': self.enum_db_id
            },
            'properties': properties
        }
        result = await self.__patch(method=method, data=data)
        return result
