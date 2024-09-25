from pydantic import BaseModel

class StaskAdd(BaseModel):
    name : str
    description : str | None = None  

class STask(StaskAdd):
    id : int

class STaskId(BaseModel):
    ok : bool
    task_id : int