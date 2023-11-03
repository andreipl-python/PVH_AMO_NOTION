from sqlite3 import Row
from typing import Optional, List

from api_models.amo_models import AMO
from api_models.notion_models import Notion
from sql import SQLiteDB


class AmoCustomField:
    def __init__(self, name: str, field_id: int, entity: str, field_type: str, enums: Optional[str], sort: int,
                 required_statuses: Optional[str], group_name: str, is_deleted: int = 0,
                 db_page_id: Optional[str] = None, enum_page_id: Optional[str] = None,
                 required_statuses_page_id: Optional[str] = None):
        self.name = name
        self.field_id = field_id
        self.entity = entity
        self.field_type = field_type
        self.enums = enums
        self.sort = sort
        self.required_statuses = required_statuses
        self.group_name = group_name
        self.is_deleted = is_deleted
        self.db_page_id = db_page_id
        self.enum_page_id = enum_page_id
        self.required_statuses_page_id = required_statuses_page_id

    def __str__(self):
        return (f"AmoCustomField(name={self.name}, field_id={self.field_id}, entity={self.entity}, "
                f"field_type={self.field_type}, enums={self.enums}, sort={self.sort}, "
                f"required_statuses={self.required_statuses}, group_name={self.group_name}, is_deleted={self.is_deleted}, "
                f"db_page_id={self.db_page_id}, enum_page_id={self.enum_page_id}, "
                f"required_statuses_page_id={self.required_statuses_page_id}")


async def get_list_of_custom_fields_objects() -> List[AmoCustomField]:
    fields_data = await AMO().get_custom_fields()
    field_objects_list = []
    for field_dict in fields_data:
        enums = None
        if field_dict.get('enums'):
            enums_list = [','.join(str(value) for value in enum.values()) for enum in field_dict.get('enums')]
            enums = ':'.join(enums_list)

        required_statuses = None
        if field_dict.get('required_statuses'):
            required_statuses_list = [','.join(str(value) for value in required_status.values())
                                      for required_status in field_dict.get('required_statuses')]
            required_statuses = ':'.join(required_statuses_list)

        field = AmoCustomField(name=field_dict.get('name'),
                               field_id=field_dict.get('id'),
                               entity=field_dict.get('entity_type'),
                               field_type=field_dict.get('type'),
                               enums=enums,
                               sort=field_dict.get('sort'),
                               required_statuses=required_statuses,
                               group_name=field_dict.get('group_id'))
        field_objects_list.append(field)

    return field_objects_list


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