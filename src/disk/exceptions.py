from pydantic import BaseModel, Field
from typing import Annotated

class Error(BaseModel):
    code : Annotated[int, Field(ge=100, lt=500, description="Код ошибки", examples=[400,404])]
    message : Annotated[str, Field(examples=["Validation Failed", "Item not found"])]

class DiskItemException(Exception):
    def __init__(self, status_code : str, e : Exception = None, info : str = None):
        self.status_code = status_code
        self.e = e
        self.info = info