from database import TasksOrm, new_session 
from tasks.schemas import STask, StaskAdd
from sqlalchemy import select
import asyncio

class TaskRepository:
    @classmethod
    async def add_one(cls, data: StaskAdd) -> int:
        async with new_session() as session:
            task_dict = data.model_dump()
            task = TasksOrm(**task_dict, test = 'test')
            session.add(task)
            await session.flush()
            await session.commit()
            return task.id
        
    @classmethod
    async def find_all(cls) -> list[STask]:
        async with new_session() as session:
            query = select(TasksOrm)
            result = await session.execute(query)
            task_models = result.scalars().all()
            task_schemas = [STask.model_validate(task_orm, from_attributes=True) for task_orm in task_models]
            return task_schemas