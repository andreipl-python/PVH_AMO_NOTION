import logging
from datetime import datetime, timedelta
from pprint import pprint
from sqlite3 import Row
from typing import List

from api_models.amo_models import AMO
from api_models.notion_models import Notion
from object_models import AmoCustomField
from sql import SQLiteDB

logger = logging.getLogger('SERVICE')


async def get_list_of_custom_fields_objects(access_token: str, refresh_token: str) -> List[AmoCustomField]:
    amo = AMO(access_token, refresh_token)
    fields_data = await amo.get_custom_fields()
    field_objects_list = []

    new_enum_counter, upd_enum_counter, new_groups_counter = 0, 0, 0
    for field_dict in fields_data:
        if field_dict.get('name') not in ['Телефон', 'Email']:
            enums = field_dict.get('enums')
            if enums:
                for enum in enums:
                    enum_id, value = enum.get('id'), enum.get('value')
                    is_enum_exist = await SQLiteDB().is_enum_exist(enum.get('id'))
                    if not is_enum_exist:
                        await SQLiteDB().insert_enum_data(enum_id=enum_id, value=value)
                        res = await Notion().insert_into_enum_db(enum_id=enum_id, value=value)
                        print(res)
                        new_enum_counter += 1
                    elif is_enum_exist:
                        sql_enum_data: List[Row] = await SQLiteDB().get_enum_data(enum_id)
                        if value != sql_enum_data[0][2]:
                            await SQLiteDB().update_enum_data(enum_id=enum_id, set_values={'value': value})
                            await Notion().update_enum_page(enum_db_page_id=sql_enum_data[0][3], value=value)
                            upd_enum_counter += 1

                enums = ':'.join([str(enum.get("id")) for enum in field_dict.get('enums')[:100]])

            group_id = field_dict.get('group_id')
            if group_id:
                is_group_exist = await SQLiteDB().is_group_exist(group_id)
                if not is_group_exist:
                    group_name = await amo.get_group_name(group_id)
                    await SQLiteDB().insert_group_data(group_id, group_name)
                    new_groups_counter += 1

            field = AmoCustomField(name=field_dict.get('name'),
                                   field_id=field_dict.get('id'),
                                   entity=field_dict.get('entity_type'),
                                   field_type=field_dict.get('type'),
                                   enums=enums,
                                   sort=field_dict.get('sort'),
                                   group_id=field_dict.get('group_id'))
            field_objects_list.append(field)

    logger.info(f'Enums Updated. Create {new_enum_counter} new enum values. Update {upd_enum_counter} enum values')
    logger.info(f'Groups Updated. Create {new_groups_counter} new group values')
    return field_objects_list


async def update_access_data() -> tuple:
    sid, access_token, create_time_str, refresh_token = await SQLiteDB().get_access_data()
    create_time = datetime.strptime(create_time_str, "%Y-%m-%d %H:%M:%S")
    amo = AMO(access_token, refresh_token)
    if not access_token or not refresh_token:
        return await amo.get_access_token_first_time()
    if datetime.now() - create_time > timedelta(hours=12):
        return await amo.get_new_access_token()
    return access_token, refresh_token


async def update_sql_table(access_token: str, refresh_token: str):
    await SQLiteDB().create_custom_fields_table()
    await SQLiteDB().create_enums_table()
    await SQLiteDB().create_groups_table()

    fields_data: List[AmoCustomField] = await get_list_of_custom_fields_objects(access_token, refresh_token)
    sql_fields_data: List[Row] = await SQLiteDB().get_all_fields_data()

    del_count, new_count, upd_count = 0, 0, 0

    if len(sql_fields_data) > len(fields_data):
        sql_field_ids = [t[2] for t in sql_fields_data]
        amo_field_ids = [obj.field_id for obj in fields_data]
        missing_field_ids = list(set(sql_field_ids) - set(amo_field_ids))
        for missing_field_id in missing_field_ids:
            await SQLiteDB().update_field_data(missing_field_id, {'is_deleted': 1})
            del_count += 1

    for field in fields_data:
        is_field_exist = await SQLiteDB().is_field_exist(field.field_id)
        if not is_field_exist:
            await SQLiteDB().insert_field_data(field)
            new_count += 1
        else:
            sql_field_data = await SQLiteDB().get_field_data(field.field_id)
            (sql_field_name, sql_field_entity, sql_field_type,
             sql_field_enums, sql_field_sort, sql_field_group_id) = (
                sql_field_data[0][1], sql_field_data[0][3], sql_field_data[0][4],
                sql_field_data[0][6], sql_field_data[0][7], sql_field_data[0][8])
            if ((field.name, field.entity, field.field_type, field.enums, field.sort, field.group_id) !=
                    (sql_field_name, sql_field_entity, sql_field_type, sql_field_enums, sql_field_sort,
                     sql_field_group_id)):
                await SQLiteDB().update_field_data_by_object(field)
                upd_count += 1

    logger.info(f'SQL Updated. Delete {del_count} rows, create {new_count} rows, update {upd_count} rows')


async def update_notion_table():
    sql_fields_data = await SQLiteDB().get_all_fields_data_for_update()
    fields_data = []
    for sql_field_data in sql_fields_data:
        field = AmoCustomField(name=sql_field_data[1], field_id=sql_field_data[2], entity=sql_field_data[3],
                               field_type=sql_field_data[4], enums=sql_field_data[6], sort=sql_field_data[7],
                               group_id=sql_field_data[8], is_deleted=sql_field_data[5], db_page_id=sql_field_data[10])
        fields_data.append(field)

    new_count, upd_count = 0, 0
    for field in fields_data:
        if not field.db_page_id:
            res = await Notion().insert_into_db(field)
            if res.get('object') == 'error':
                logger.error(f'Fail create row in Notion! Field ID: {field.field_id}, Field Entity: {field.entity}, '
                             f'Message: {res.get("message")}')
            else:
                new_count += 1
                await SQLiteDB().set_unmodified_field(field.field_id)
        elif field.db_page_id:
            res = await Notion().update_db_page(field)
            if res.get('object') == 'error':
                logger.error(f'Fail update row in Notion! Field ID: {field.field_id}, Field Entity: {field.entity}, '
                             f'Message: {res.get("message")}')
            else:
                upd_count += 1
                await SQLiteDB().set_unmodified_field(field.field_id)

    logger.info(f'Notion Updated. Create {new_count} rows, update {upd_count} rows')
