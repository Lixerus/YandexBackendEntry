from src.database import DiskFolderOrm, DiskHistoryItems
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, aliased
from sqlalchemy import select, Sequence, delete, func
from src.disk.schemas import DiskItemImportSchema, DiskItemRetreweSchema, HistoryResponse
from datetime import datetime, timedelta
from src.disk.schemas import SysItemType
from sqlalchemy.exc import NoResultFound
from src.disk.exceptions import DiskItemException

class DiskItemService:
    @classmethod
    async def persist_diskitems(cls, diskitems : list[DiskItemImportSchema], date: datetime, session : AsyncSession) -> None:
        db_items : list[DiskFolderOrm] = await cls._validate_type(diskitems, session)
        new_db_parents : list[DiskFolderOrm] = await cls._validate_parent_type(diskitems, session)
        update_data , insert_data = cls._split_update_insert(diskitems, db_items, date)
        cls._build_orm_relations(insert_data, session)
        await session.flush()
        all_parents_ids = {item.parentId for item in db_items}.union({item.id for item in new_db_parents})
        all_ancestors_for_idmap = await DiskFolderOrm.load_ancestors(all_parents_ids, session)
        await cls._apply_update(db_items, update_data, session, date)
        for new_orm_item in insert_data.values():
            if new_orm_item.item_type != SysItemType.FOLDER and new_orm_item.parentId != None:
                new_orm_item.parent.update_loaded_parents_size(new_orm_item.size, new_orm_item.date)
        cls._add_all_diskitem_to_history(session)

    @classmethod
    def _add_all_diskitem_to_history(cls, session: AsyncSession) -> None: 
        session.add_all([DiskHistoryItems(
            **{column.name : getattr(item, column.name) for column in DiskFolderOrm.__table__.columns}
            ) 
            for item in session.identity_map.values()])
    
    @classmethod
    async def _apply_update(
        cls, db_items : list[DiskFolderOrm], update_data : dict[str, DiskItemImportSchema], 
        session : AsyncSession, date : datetime
        ) -> None:
        for db_old_item in db_items:
            db_old_item.date = date
            new_item_data = update_data.get(db_old_item.id)
            assert new_item_data != None
            if new_item_data.item_type == SysItemType.FOLDER:
                assert new_item_data.size == 0
                new_item_data.size = db_old_item.size
            if db_old_item.parentId != new_item_data.parentId:
                await cls._handle_different_parents_update(db_old_item, session, db_old_item.parentId, db_old_item.size, new_item_data.parentId, new_item_data.size)
            elif db_old_item.parentId != None:
                db_old_item.parent.update_loaded_parents_size(new_item_data.size - db_old_item.size, db_old_item.date)
            db_old_item.update(**new_item_data.model_dump())

    @classmethod
    async def _handle_different_parents_update(
        cls, db_item : DiskFolderOrm, session : AsyncSession, old_parent_id : str,
        old_size : int, new_parent_id : str, new_size : str
        ) -> None:
        if old_parent_id != None:
            old_parent = db_item.parent
            old_parent.update_loaded_parents_size(-old_size, db_item.date)
        if new_parent_id != None:
            new_parent = await session.get(DiskFolderOrm, new_parent_id)
            new_parent.update_loaded_parents_size(new_size, db_item.date)
            db_item.parent = new_parent

    @classmethod
    def _build_orm_relations(cls, items_dict : dict[str, DiskFolderOrm], session : AsyncSession) -> None:
        for item in items_dict.values():
            if item.parentId != None and (p := items_dict.get(item.parentId)) != None:
                item.parent = p
            session.add(item)

    @classmethod
    def _split_update_insert(
        cls, request_items : list[DiskItemImportSchema], db_items : list[DiskFolderOrm], date:datetime = datetime
        ) -> tuple[dict[str,DiskItemImportSchema],dict[str,DiskFolderOrm]]:
        update_data : dict[str, DiskItemImportSchema] = dict()
        insert_data : dict[str, DiskFolderOrm] = dict()
        db_items_ids = {item.id for item in db_items}
        for item in request_items:
            if item.id in db_items_ids:
                update_data[item.id] = item
            else:
                insert_data[item.id] = DiskFolderOrm(**item.model_dump(), date=date)
                print(insert_data[item.id].date)
        return update_data , insert_data

    @classmethod
    async def _validate_type(cls, request_items : list[DiskItemImportSchema], session : AsyncSession) -> Sequence[DiskFolderOrm]:
        request_id_type = {item.id : item.item_type for item in request_items}
        items_q = select(DiskFolderOrm).where(DiskFolderOrm.id.in_(request_id_type.keys()))#.options(selectinload(DiskFolderOrm.parent))
        db_items_res = await session.execute(items_q)
        db_items = db_items_res.scalars().all()
        for db_item in db_items:
            if request_id_type.get(db_item.id) != db_item.item_type:
                raise DiskItemException(status_code=400, info = f"item with id {db_item.id} cannot change type")
        return db_items 

    @classmethod
    async def _validate_parent_type(cls, request_items : list[DiskItemImportSchema], session : AsyncSession) -> Sequence[DiskFolderOrm]:
        request_items_parents_ids = {item.parentId for item in request_items}
        all_items_ids = {item.id for item in request_items}
        request_items_parents_ids.discard(None)
        parents_q = select(DiskFolderOrm).where(DiskFolderOrm.id.in_(request_items_parents_ids))
        db_items_res = await session.execute(parents_q)
        db_parents = db_items_res.scalars().all()
        for db_parent in db_parents:
            request_items_parents_ids.remove(db_parent.id)
            if db_parent.item_type != SysItemType.FOLDER:
                raise  DiskItemException(status_code=400, info =f"item with id {db_parent.id} cannot be parent. FOLDER type required")
        for parentId in request_items_parents_ids:
            if parentId not in all_items_ids:
                raise  DiskItemException(status_code=400, info =f"item with id : {parentId} doesnt exist")
        return db_parents

    @classmethod
    async def delete_item(cls, id : str, date: datetime, session: AsyncSession) -> None:
        delete_item = await session.get(DiskFolderOrm, id)
        if delete_item == None:
            raise DiskItemException(status_code=404, info = "No item")
        if (p := delete_item.parentId) != None:
            ancestors = await DiskFolderOrm.load_ancestors({p}, session)
            size = int(delete_item.size or 0)
            for ancestor in ancestors:
                ancestor.date = date
                ancestor.size =  int(ancestor.size or 0) - size
        await session.delete(delete_item) # existing trigger deletes all history rows affected after ON CASCADE delete
        delete_history_q = delete(DiskHistoryItems).where(DiskHistoryItems.id == id)
        await session.execute(delete_history_q)
        cls._add_all_diskitem_to_history(session)
        return 
    
    @classmethod
    async def get_item(cls, id: str, session: AsyncSession) -> DiskItemRetreweSchema:
        try:
            retreve_item = await session.get_one(DiskFolderOrm, id, options=[selectinload(DiskFolderOrm.children, recursion_depth=0)])
        except NoResultFound:
            raise DiskItemException(status_code=404, info = "No item")
        children_stack = [item for item in retreve_item.children]
        while len(children_stack) != 0:
            new_child = children_stack.pop()
            for child in await new_child.awaitable_attrs.children:
                children_stack.append(child)
        item_schema = DiskItemRetreweSchema.model_validate(retreve_item)
        return item_schema

    @classmethod
    async def get_update_24h(cls, date, session: AsyncSession) -> HistoryResponse:
        start_date = date - timedelta(days=1)
        partition_cte = select(DiskHistoryItems, 
                func.dense_rank().over(partition_by=DiskHistoryItems.id, order_by=DiskHistoryItems.date.desc()).label('recent')
            ).where(DiskHistoryItems.item_type == SysItemType.FILE).where(DiskHistoryItems.date.between(start_date, date))\
            .cte('history')
        aliased_history_tbl = aliased(DiskHistoryItems, partition_cte)
        updates_q = select(aliased_history_tbl).select_from(partition_cte).where(partition_cte.c.recent == 1)
        results = await session.execute(updates_q)
        data_orm = results.scalars().all()
        response = HistoryResponse.model_validate({"items" : data_orm})
        return response
    
    @classmethod
    async def get_history(cls, id : str, dateStart : datetime, dateEnd : datetime, session: AsyncSession) -> HistoryResponse:
        history_udates_q = select(DiskHistoryItems).where(DiskHistoryItems.id == id)\
            .where(DiskHistoryItems.date.__ge__(dateStart)).where(DiskHistoryItems.date.__lt__(dateEnd))
        print(id, dateStart, dateEnd)
        print(history_udates_q.compile(compile_kwargs={"literal_binds": True}))
        results = await session.execute(history_udates_q)
        print(results)
        data_orm = results.scalars().all()
        print(data_orm)
        if len(data_orm) == 0:
            raise DiskItemException(status_code=404, info = "No item")
        response = HistoryResponse.model_validate({"items" : data_orm})
        return response