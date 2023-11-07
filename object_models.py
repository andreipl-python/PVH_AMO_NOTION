from typing import Optional


class AmoCustomField:
    def __init__(self, name: str, field_id: int, entity: str, field_type: str, enums: Optional[str], sort: int,
                 group_id: Optional[str], is_deleted: int = 0, db_page_id: Optional[str] = None):
        self.name = name
        self.field_id = field_id
        self.entity = entity
        self.field_type = field_type
        self.enums = enums
        self.sort = sort
        self.group_id = group_id
        self.is_deleted = is_deleted
        self.db_page_id = db_page_id

    def __str__(self):
        return (f"AmoCustomField(name={self.name}, field_id={self.field_id}, entity={self.entity}, "
                f"field_type={self.field_type}, enums={self.enums}, sort={self.sort}, "
                f"group_id={self.group_id}, is_deleted={self.is_deleted}, db_page_id={self.db_page_id})")
