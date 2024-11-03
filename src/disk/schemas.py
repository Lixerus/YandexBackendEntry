from pydantic import (
    BaseModel, 
    ConfigDict,
    ValidationInfo,
    Field, 
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
    size : Annotated[Optional[int], Field(ge=0, default=0)]

    @model_validator(mode='after')
    def foldertype_validator(self) -> Self:
        if self.item_type == SysItemType.FOLDER:
            if self.url != None:
                raise ValueError(f"url not null in folder with id {self.id}")
            if self.size != None:
                raise ValueError(f"size not null in folder with id {self.id}")
            # set 0 to size if no ValueError raised on FOLDER type
            self.size = 0
        else:
            if self.url == None:
                raise ValueError(f"url null in file with id {self.id}")
            if self.size == None or self.size <= 0:
                raise ValueError(f"size null or le 0 with file id {self.id}")
        return self

def set_children_to_none(value: list['DiskItemRetreweSchema'], info : ValidationInfo) -> list[DiskItemImportSchema] | None:
    if len(value) == 0:
        return None
    return value

class DiskItemRetreweSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id : str
    url : Optional[str]
    date : datetime
    parentId : Optional[str]
    item_type : Annotated[SysItemType,  Field(alias='type')]
    size : Optional[int]
    children : Annotated[
        Optional[list['DiskItemRetreweSchema']], AfterValidator(set_children_to_none), Field(examples=[None])]




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
        if item.parentId != None and type_dict.get(item.parentId, SysItemType.FOLDER)!= SysItemType.FOLDER:
            raise AssertionError(f"Parent of item with id {item.id} cannot be type ""FILE""")
    return value

class DiskItemsDTO(BaseModel):
    items : Annotated[list[DiskItemImportSchema], AfterValidator(validate_nonrepeat_id), AfterValidator(validate_parent_folder)]
    updateDate : datetime

class DiskItemHistorySchema(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id : str
    url : Optional[str]
    date : datetime
    parentId : Optional[str]
    item_type : Annotated[SysItemType,  Field(alias='type')]
    size : Optional[int]

class HistoryResponse(BaseModel):
    items: list[DiskItemHistorySchema] | None