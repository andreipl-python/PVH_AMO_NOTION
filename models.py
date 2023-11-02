from typing import Optional, List

from api_models.amo_models import AMO


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
