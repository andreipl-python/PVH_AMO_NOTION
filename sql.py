import aiosqlite

from service.models import AmoCustomField


class SQLiteDB:
    def __init__(self, db_path):
        self.db_path = db_path

    async def execute_query(self, query, *args):
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.cursor()
            await cursor.execute(query, args)
            await db.commit()
            await cursor.close()

    async def fetch_query(self, query, *args):
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.cursor()
            await cursor.execute(query, args)
            rows = await cursor.fetchall()
            await cursor.close()
            return rows

    async def create_custom_fields_table(self):
        query = '''CREATE TABLE IF NOT EXISTS custom_fields (id INTEGER PRIMARY KEY, name TEXT, field_id INTEGER, 
        entity TEXT, field_type TEXT, is_deleted INTEGER, enums TEXT, sort INTEGER, required_statuses TEXT, 
        group_name TEXT, modified INTEGER, db_page_id TEXT);'''
        await self.execute_query(query)

    async def insert_field_data(self, field: AmoCustomField):
        pass
