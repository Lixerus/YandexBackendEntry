from database import new_session, DiskFolderOrm, DiskHistoryItems
from .schemas import SysItemType
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased
from sqlalchemy import select
from disk.schemas import DiskItemImportSchema
from datetime import datetime
from fastapi.exceptions import RequestValidationError

class DiskItemRepository:
    @classmethod
    async def persist_diskitems(cls, diskitems : list[DiskItemImportSchema], date: datetime, save_histroy : bool = True) -> None:
        async with new_session() as session:
            for item in diskitems:
                await DiskItemRepository.__perform_item_update_date(item, session, date, save_histroy)
            await session.commit()

    @classmethod
    def __add_diskitem_to_history(cls, item : DiskItemImportSchema, session: AsyncSession, date) -> None: 
        session.add(DiskHistoryItems(**item.model_dump(by_alias=False), date=date))

    @classmethod
    async def __perform_item_update_date(cls, item : DiskItemImportSchema , session: AsyncSession, date : datetime, save_histroy : bool = True):
        orm_item = await session.get(DiskFolderOrm, item.id)
        print("ORM ITEM!!!!!!!!!!!!!", orm_item)
        if orm_item == None:
            session.add(DiskFolderOrm(**item.model_dump(), date = date))
            if save_histroy:
                DiskItemRepository.__add_diskitem_to_history(item, session, date)
            await DiskItemRepository.__perform_folder_update(item.parentId, session, int(item.size or 0), date)
            return
        orm_item.update(**item.model_dump(), date = date)
        
        if orm_item.item_type != item.item_type:
            raise RequestValidationError("Type cannot be changed")
        elif orm_item.parentId == item.parentId:
            diff = int(item.size or 0) - int(orm_item.size or 0)
            await DiskItemRepository.__perform_folder_update(orm_item.parentId, session, diff, date)
        else:
            await DiskItemRepository.__perform_folder_update(orm_item.parentId, session, -orm_item.size, date)
            await DiskItemRepository.__perform_folder_update(item.parentId, session, item.size, date)
        if save_histroy:
            DiskItemRepository.__add_diskitem_to_history(item, session, date)
        return
        


    @classmethod
    async def __perform_folder_update(cls, id, session : AsyncSession, value, date, save_history=True):
        rec_cte_basis = select(DiskFolderOrm).where(DiskFolderOrm.id==id).cte(name="rec", recursive=True)
        rec_cte_condition = select(DiskFolderOrm).join(rec_cte_basis, DiskFolderOrm.id == rec_cte_basis.c.parentId)
        ancestors = rec_cte_basis.union_all(rec_cte_condition)
        ancestors_cte = aliased(DiskFolderOrm, ancestors)
        result = await session.execute(select(ancestors_cte).select_from(ancestors_cte))
        t = result.scalars().all()
        print(t)
        for item in t:
            item.date = date
            item.size = int(item.size or 0) + value
            if save_history:
                session.add(DiskHistoryItems(id = item.id, date = item.date, url = item.url, size = item.size, parentId = item.parentId, item_type = item.item_type))