from typing import Annotated
from fastapi import APIRouter, Depends


from tasks.repository import TaskRepository
from tasks.schemas import STask, StaskAdd, STaskId

router = APIRouter(
    prefix = "/tasks",
    tags=['Таски',]
)

@router.post("")
async def add_task(
    task : Annotated[StaskAdd, Depends()]
)-> STaskId:
    task_id = await TaskRepository.add_one(task)
    return {"ok" : True, "task_id" : task_id}


@router.get('')
async def get_tasks() -> list[STask]:
    tasks = await TaskRepository.find_all()
    return tasks
