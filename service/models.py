from typing import Optional, List
from api_models.amo_models import AMO


class AmoCustomField:
    def __init__(self, name: str, field_id: int, entity: str, field_type: str, enums: Optional[str], sort: int,
                 required_statuses: Optional[str], group_name: str):
        self.name = name
        self.field_id = field_id
        self.entity = entity
        self.field_type = field_type
        self.enums = enums
        self.sort = sort
        self.required_statuses = required_statuses
        self.group_name = group_name


async def get_list_of_custom_fields_objects() -> List[AmoCustomField]:
    fields_data = await AMO().get_custom_fields()
    field_objects_list = []
    for field_dict in fields_data:
        enums = None
        if field_dict.get('enums'):
            enums_list = [','.join(enum.values()) for enum in field_dict.get('enums')]
            enums = ':'.join(enums_list)

        required_statuses = None
        if field_dict.get('required_statuses'):
            required_statuses_list = [','.join(required_status.values()) for required_status in
                                      field_dict.get('required_statuses')]
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
