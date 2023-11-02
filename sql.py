import asyncio
from sqlite3 import Row
from typing import List

import aiosqlite

from models import AmoCustomField


class SQLiteDB:
    def __init__(self):
        self.db_path = 'database.db'

    async def execute_query(self, query, *args):
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.cursor()
            await cursor.execute(query, args)
            await db.commit()
            await cursor.close()

    async def fetch_query(self, query, *args) -> List[Row]:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.cursor()
            await cursor.execute(query, args)
            rows = await cursor.fetchall()
            await cursor.close()
            return rows

    async def create_custom_fields_table(self) -> None:
        query = '''CREATE TABLE IF NOT EXISTS custom_fields (id INTEGER PRIMARY KEY, name TEXT, field_id INTEGER, 
        entity TEXT, field_type TEXT, is_deleted INTEGER, enums TEXT, sort INTEGER, required_statuses TEXT, 
        group_name TEXT, modified INTEGER, db_page_id TEXT, enum_page_id TEXT, required_statuses_page_id TEXT);'''
        return await self.execute_query(query)

    async def is_field_exist(self, field_id: int) -> bool:
        query = 'SELECT * FROM custom_fields WHERE field_id = ?;'
        return bool(await self.fetch_query(query, field_id))

    async def get_all_fields_data(self) -> List[Row]:
        query = 'SELECT * FROM custom_fields WHERE is_deleted = 0;'
        return await self.fetch_query(query)

    async def get_all_fields_data_for_update(self) -> List[Row]:
        query = 'SELECT * FROM custom_fields WHERE modified = 1;'
        return await self.fetch_query(query)

    async def get_field_data(self, field_id: int) -> List[Row]:
        query = 'SELECT * FROM custom_fields WHERE field_id = ?;'
        return await self.fetch_query(query, field_id)

    async def insert_field_data(self, field: AmoCustomField) -> None:
        query = '''INSERT INTO custom_fields (name, field_id, entity, field_type, is_deleted, enums, sort, 
        required_statuses, group_name, modified, db_page_id, enum_page_id, required_statuses_page_id) VALUES 
        (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);'''
        insert_values = (field.name, field.field_id, field.entity, field.field_type, 0, field.enums, field.sort,
                         field.required_statuses, field.group_name, 1, None, None, None)
        return await self.execute_query(query, *insert_values)

    async def update_field_data(self, field_id: int, set_values: dict):
        set_values_str = ', '.join([f'{column} = ?' for column in set_values.keys()]) + ', modified = 1'
        query = f'UPDATE custom_fields SET {set_values_str} WHERE field_id = {field_id};'
        print(query)
        print(*set_values.values())
        await self.execute_query(query, *set_values.values())

    async def update_field_data_by_object(self, field: AmoCustomField):
        query = f'''UPDATE custom_fields SET name = ?, entity = ?, field_type = ?, enums = ?, sort = ?, 
        required_statuses = ?, group_name = ?, modified = 1 WHERE field_id = ?;'''
        insert_values = (field.name, field.entity, field.field_type, field.enums, field.sort, field.required_statuses,
                         field.group_name, field.field_id)
        await self.execute_query(query, *insert_values)

#
# async def main():
#     res = await SQLiteDB().update_field_data(1001887, {'db_page_id': 'blblblblb'})
#     print(res)
#
#
# asyncio.run(main())
