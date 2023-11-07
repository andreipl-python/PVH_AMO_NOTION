import asyncio
import datetime
from sqlite3 import Row
from typing import List, Union, Optional

import aiosqlite

from object_models import AmoCustomField


class SQLiteDB:
    def __init__(self):
        self.db_path = 'database.db'

    async def execute_query(self, query, *args):
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.cursor()
            await cursor.execute(query, args)
            await db.commit()
            await cursor.close()

    async def fetch_query(self, query, *args) -> Optional[Union[List[Row], tuple]]:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.cursor()
            await cursor.execute(query, args)
            rows = await cursor.fetchall()
            await cursor.close()
            return rows

    async def get_access_data(self) -> List[tuple]:
        check_table_query = '''SELECT count(*) FROM sqlite_master WHERE type='table' AND name='access';'''
        result = await self.fetch_query(check_table_query)
        table_exists = result[0][0] > 0

        if not table_exists:
            create_table_query = '''CREATE TABLE access (
                            id INTEGER PRIMARY KEY,
                            access_token TEXT,
                            create_time TEXT,
                            refresh_token TEXT
                        )'''
            await self.execute_query(create_table_query)

            insert_query = '''INSERT INTO access (access_token, create_time, refresh_token) VALUES (?, ?, ?)'''
            insert_values = (None, '2000-01-01 10:00:00', None)
            await self.execute_query(insert_query, *insert_values)
        query = '''SELECT * FROM access'''
        result = await self.fetch_query(query)
        return result[0]

    async def update_access_data(self, access_token: str, refresh_token: str):
        time_now = datetime.datetime.now()
        string_date = time_now.strftime("%Y-%m-%d %H:%M:%S")
        query = 'UPDATE access SET access_token = ?, create_time = ?, refresh_token = ?;'
        insert_values = (access_token, string_date, refresh_token)
        return await self.execute_query(query, *insert_values)

    async def create_custom_fields_table(self) -> None:
        query = '''CREATE TABLE IF NOT EXISTS custom_fields 
        (id INTEGER PRIMARY KEY, 
        name TEXT, 
        field_id INTEGER, 
        entity TEXT, 
        field_type TEXT, 
        is_deleted INTEGER, 
        enums TEXT, 
        sort INTEGER, 
        group_id TEXT, 
        modified INTEGER, 
        db_page_id TEXT);'''
        return await self.execute_query(query)

    async def create_enums_table(self) -> None:
        query = '''CREATE TABLE IF NOT EXISTS enums 
        (id INTEGER PRIMARY KEY, 
        enum_id INTEGER, 
        value TEXT, 
        db_page_id TEXT);'''
        return await self.execute_query(query)

    async def create_groups_table(self) -> None:
        query = '''CREATE TABLE IF NOT EXISTS groups
        (id INTEGER PRIMARY KEY,
        group_id TEXT,
        group_name TEXT);'''
        return await self.fetch_query(query)

    async def is_field_exist(self, field_id: int) -> bool:
        query = 'SELECT * FROM custom_fields WHERE field_id = ?;'
        return bool(await self.fetch_query(query, field_id))

    async def is_enum_exist(self, enum_id: int) -> bool:
        query = 'SELECT * FROM enums WHERE enum_id = ?;'
        return bool(await self.fetch_query(query, enum_id))

    async def is_group_exist(self, group_id: str) -> bool:
        query = 'SELECT * FROM groups WHERE group_id = ?;'
        return bool(await self.fetch_query(query, group_id))

    async def get_all_fields_data(self) -> List[Row]:
        query = 'SELECT * FROM custom_fields WHERE is_deleted = 0;'
        return await self.fetch_query(query)

    async def get_all_fields_data_for_update(self) -> List[Row]:
        query = 'SELECT * FROM custom_fields WHERE modified = 1;'
        return await self.fetch_query(query)

    async def get_field_data(self, field_id: int) -> List[Row]:
        query = 'SELECT * FROM custom_fields WHERE field_id = ?;'
        return await self.fetch_query(query, field_id)

    async def get_enum_data(self, enum_id: int) -> List[Row]:
        query = 'SELECT * FROM enums WHERE enum_id = ?;'
        return await self.fetch_query(query, enum_id)

    async def get_group_data(self, group_id: str) -> List[Row]:
        query = 'SELECT * FROM groups WHERE group_id = ?;'
        return await self.fetch_query(query, group_id)

    async def insert_field_data(self, field: AmoCustomField) -> None:
        query = '''INSERT INTO custom_fields (name, field_id, entity, field_type, is_deleted, enums, sort, 
        group_id, modified, db_page_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);'''
        insert_values = (field.name, field.field_id, field.entity, field.field_type, 0, field.enums, field.sort,
                         field.group_id, 1, None)
        return await self.execute_query(query, *insert_values)

    async def insert_enum_data(self, enum_id: int, value: str) -> None:
        query = '''INSERT INTO enums (enum_id, value) VALUES (?, ?);'''
        return await self.execute_query(query, enum_id, value)

    async def insert_group_data(self, group_id: str, group_name: str) -> None:
        query = '''INSERT INTO groups (group_id, group_name) VALUES (?, ?);'''
        return await self.execute_query(query, group_id, group_name)

    async def update_field_data(self, field_id: int, set_values: dict) -> None:
        set_values_str = ', '.join([f'{column} = ?' for column in set_values.keys()]) + ', modified = 1'
        query = f'UPDATE custom_fields SET {set_values_str} WHERE field_id = {field_id};'
        await self.execute_query(query, *set_values.values())

    async def set_unmodified_field(self, field_id: int) -> None:
        query = 'UPDATE custom_fields SET modified = 0 WHERE field_id = ?;'
        await self.execute_query(query, field_id)

    async def update_enum_data(self, enum_id: int, set_values: dict):
        set_values_str = ', '.join([f'{column} = ?' for column in set_values.keys()])
        query = f'UPDATE enums SET {set_values_str} WHERE enum_id = {enum_id};'
        await self.execute_query(query, *set_values.values())

    async def update_field_data_by_object(self, field: AmoCustomField):
        query = f'''UPDATE custom_fields SET name = ?, entity = ?, field_type = ?, enums = ?, sort = ?, 
        group_id = ?, modified = 1 WHERE field_id = ?;'''
        insert_values = (field.name, field.entity, field.field_type, field.enums, field.sort, field.group_id,
                         field.field_id)
        await self.execute_query(query, *insert_values)

#
# async def main():
#     res = await SQLiteDB().update_field_data(1001887, {'db_page_id': 'blblblblb'})
#     print(res)
#
#
# asyncio.run(main())
