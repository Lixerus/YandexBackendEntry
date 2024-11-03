from __future__ import annotations
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncAttrs, AsyncSession
from sqlalchemy.orm import aliased
from sqlalchemy import (
    ForeignKey,
    String,
    CheckConstraint,
    # PrimaryKeyConstraint,
    Index,
    event,
    DDL,
    select,
)
from sqlalchemy.orm import(
    DeclarativeBase,
    Mapped,
    relationship,
    mapped_column,
    validates,
)
from typing import List
from .disk.schemas import SysItemType
from datetime import datetime

aengine = create_async_engine("sqlite+aiosqlite:///db_data/tasks.db", echo=True)
new_session = async_sessionmaker(aengine, expire_on_commit=False, autoflush=True)

@event.listens_for(aengine.sync_engine, "connect")
def enable_sqlite_fks(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

class Model(AsyncAttrs,DeclarativeBase):
    pass

class DiskFolderOrm(Model):
    __tablename__ = "disk_folders_table"
    __table_args__ = (
         CheckConstraint("size >= 0", name="positive_size"),
    )
    id : Mapped[str] = mapped_column(primary_key=True, autoincrement=False)
    url : Mapped[str | None] = mapped_column(String(255))
    size : Mapped[int | None]
    item_type : Mapped[SysItemType]
    date : Mapped[datetime]
    parentId : Mapped[str | None] = mapped_column(ForeignKey('disk_folders_table.id', ondelete="CASCADE"))
    parent : Mapped[DiskFolderOrm | None] = relationship(back_populates='children', remote_side=[id], lazy='raise_on_sql')
    children : Mapped[List[DiskFolderOrm]] = relationship(back_populates='parent', cascade="all, delete", passive_deletes=True)

    # def __repr__(self) -> str:
    #     return f"{self.id}, {self.item_type}, {self.date}, {self.size}, {self.parentId}"
    
    @validates('size')
    def validate_size(self, key, size, *args):
        if size != None and size < 0:
            raise ValueError("Size must be none or ge than 0")
        return size
    
    @classmethod
    async def load_ancestors(cls, parents : set, session : AsyncSession) -> list[DiskFolderOrm]:
        parents.discard(None)
        rec_cte_basis = select(DiskFolderOrm).where(DiskFolderOrm.id.in_(parents)).cte(name="rec", recursive=True)
        rec_cte_condition = select(DiskFolderOrm).join(rec_cte_basis, DiskFolderOrm.id == rec_cte_basis.c.parentId)
        ancestors = rec_cte_basis.union(rec_cte_condition)
        ancestors_cte = aliased(DiskFolderOrm, ancestors)
        result = await session.execute(select(ancestors_cte).select_from(ancestors_cte))
        ancestors = result.scalars().all()
        return ancestors
    
    def update(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        
    def update_loaded_parents_size(self, size_diff : int, date : datetime):
        self.size += size_diff
        self.date = date
        temp = self
        while temp.parentId != None:
            temp.parent.size += size_diff
            temp.parent.date = date
            temp = temp.parent


class DiskHistoryItems(Model):
    __tablename__ = "disk_history"
    pk : Mapped[int] = mapped_column(primary_key=True)
    id : Mapped[str]
    url : Mapped[str | None]
    parentId : Mapped[str | None]
    size : Mapped[int | None]
    item_type : Mapped[SysItemType]
    date : Mapped[datetime]

    __table_args__ = (
        Index('ix_id', 'id'),
        #PrimaryKeyConstraint('id', 'date', name="history_items_pk"),
    )

delete_history_tr = DDL('''\
CREATE TRIGGER IF NOT EXISTS delete_history AFTER DELETE ON disk_folders_table
  BEGIN
    DELETE FROM disk_history WHERE (id = old.id);
  END;''')

async def create_tables():
    async with aengine.begin() as conn:
        await conn.run_sync(Model.metadata.create_all)
        await conn.execute(delete_history_tr)

# async def delete_tables():
#     async with aengine.begin() as conn:
#         await conn.execute(DDL("DROP TRIGGER IF EXISTS delete_history;"))
#         await conn.run_sync(Model.metadata.drop_all)