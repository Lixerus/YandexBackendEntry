from pydantic import (
    BaseModel, 
    ConfigDict,
    ValidationInfo,
    Field, 
    field_validator,
    model_validator,
    AfterValidator,
)

from typing import Annotated, Optional, Self
from datetime import datetime
from enum import Enum

class SysItemType(str, Enum):
    FILE = "FILE"
    FOLDER = "FOLDER"


class DiskItemImportSchema(BaseModel):
    id : str
    url : Annotated[Optional[str], Field(min_length=0, max_length=255, default=None)]
    parentId : Optional[str]
    item_type : Annotated[SysItemType, Field(alias='type')]
    size : Annotated[Optional[int], Field(ge=0, default=None)]

    @model_validator(mode='after')
    def foldertype_validator(self) -> Self:
        if self.item_type == SysItemType.FOLDER:
            if self.url != None:
                raise ValueError(f"url not null in folder with id {self.id}")
            if self.size != None:
                raise ValueError(f"size not null in folder with id {self.id}")
        return self

    # @field_validator('date', mode='before')
    # @classmethod
    # def add_datetime(cls, unvalidated_data : Any, info : ValidationInfo) -> Any:
    #     try:
    #         print(unvalidated_data, type(unvalidated_data), "IN validator")
    #         safe_date = info.context.get('updateDate')
    #     except KeyError as e:
    #         raise ValidationError("No timedate key")
    #     unvalidated_data['date'] = safe_date
    #     return unvalidated_data
    

class DiskItemRetreweSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id : str
    url : Optional[str]
    date : datetime
    parentId : Optional[str]
    type : SysItemType
    size : Optional[str]
    children : list['DiskItemRetreweSchema']


def validate_nonrepeat_id(value: list[DiskItemImportSchema], info : ValidationInfo) -> list[DiskItemImportSchema]:
    ids = set([item.id for item in value])
    if len(ids) != len(value):
        raise ValueError("Multiple indentical ids")
    return value

def validate_parent_folder(value: list[DiskItemImportSchema], info : ValidationInfo) -> list[DiskItemImportSchema]:
    type_dict = {item.id : item.item_type for item in value}
    for item in value:
        if item.parentId == item.id:
            raise AssertionError(f"Cannot be parent of yourself")
        if item.parentId != None and type_dict[item.parentId] != SysItemType.FOLDER:
            raise AssertionError(f"Parent of item with id {item.id} cannot be type ""FILE""")
    return value

class DiskItemsDTO(BaseModel):
    items : Annotated[list[DiskItemImportSchema], AfterValidator(validate_nonrepeat_id), AfterValidator(validate_parent_folder)]
    updateDate : datetime
