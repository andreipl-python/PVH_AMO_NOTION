import asyncio
from sqlite3 import Row
from typing import List

from api_models.notion_models import Notion
from models import AmoCustomField
from models import get_list_of_custom_fields_objects
from sql import SQLiteDB


async def update_sql_table():
    await SQLiteDB().create_custom_fields_table()

    fields_data: List[AmoCustomField] = await get_list_of_custom_fields_objects()
    sql_fields_data: List[Row] = await SQLiteDB().get_all_fields_data()

    if len(sql_fields_data) > len(fields_data):
        sql_field_ids = [t[2] for t in sql_fields_data]
        amo_field_ids = [obj.field_id for obj in fields_data]
        missing_field_ids = list(set(sql_field_ids) - set(amo_field_ids))
        for missing_field_id in missing_field_ids:
            await SQLiteDB().update_field_data(missing_field_id, {'is_deleted': 1})
            print(f'Удалил запись ID {missing_field_id}')

    for field in fields_data:
        is_field_exist = await SQLiteDB().is_field_exist(field.field_id)
        if not is_field_exist:
            await SQLiteDB().insert_field_data(field)
            print(f'Создал запись ID {field.field_id}')
        else:
            sql_field_data = await SQLiteDB().get_field_data(field.field_id)
            (sql_field_name, sql_field_entity, sql_field_type,
             sql_field_enums, sql_field_sort, sql_field_required_statuses,
             sql_field_group_name) = (sql_field_data[0][1], sql_field_data[0][3], sql_field_data[0][4],
                                      sql_field_data[0][6], sql_field_data[0][7], sql_field_data[0][8],
                                      sql_field_data[0][9])
            if (field.name, field.entity, field.field_type, field.enums, field.sort, field.required_statuses,
                field.group_name) != (sql_field_name, sql_field_entity, sql_field_type, sql_field_enums,
                                      sql_field_sort, sql_field_required_statuses, sql_field_group_name):
                await SQLiteDB().update_field_data_by_object(field)
                print(f'Обновил запись ID {field.field_id}')


async def update_notion_table():
    sql_fields_data = await SQLiteDB().get_all_fields_data_for_update()
    fields_data = []
    for sql_field_data in sql_fields_data:
        field = AmoCustomField(name=sql_field_data[1], field_id=sql_field_data[2], entity=sql_field_data[3],
                               field_type=sql_field_data[4], enums=sql_field_data[6], sort=sql_field_data[7],
                               required_statuses=sql_field_data[8], group_name=sql_field_data[9],
                               is_deleted=sql_field_data[5], db_page_id=sql_field_data[11],
                               enum_page_id=sql_field_data[12], required_statuses_page_id=sql_field_data[13])
        fields_data.append(field)

    count = 0
    for field in fields_data:
        if not field.db_page_id:
            await Notion().insert_into_db(field)
            count += 1
            print(f'Create row {count} for {field}')


async def main():
    await update_sql_table()
    await update_notion_table()

asyncio.run(main())

