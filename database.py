from __future__ import annotations
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import (
    ForeignKey,
    String,
    CheckConstraint,
    PrimaryKeyConstraint,
)
from sqlalchemy.orm import(
    DeclarativeBase,
    Mapped,
    relationship,
    mapped_column,
    validates,
)
from typing import List
from disk.schemas import SysItemType
from datetime import datetime

aengine = create_async_engine("sqlite+aiosqlite:///tasks.db", echo=True)

new_session = async_sessionmaker(aengine, expire_on_commit=False)

class Model(DeclarativeBase):
    pass

class TasksOrm(Model):
    __tablename__ = "tasks_table"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    description: Mapped[str | None]
    test : Mapped[str | None]


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
    parentId : Mapped[str | None] = mapped_column(ForeignKey('disk_folders_table.id'))
    parent : Mapped[DiskFolderOrm | None] = relationship(back_populates='children', remote_side=[id])
    children : Mapped[List[DiskFolderOrm]] = relationship(back_populates='parent')

    def update(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    @validates('size')
    def validate_size(self, key, size, *args):
        if size != None and size < 0:
            raise ValueError("Size must be none or ge than 0")
        return size
    


class DiskHistoryItems(Model):
    __tablename__ = "disk_history"
    pk : Mapped[int] =  mapped_column(primary_key=True, autoincrement=True)

    id : Mapped[str] #= mapped_column(primary_key=True, autoincrement=False)
    url : Mapped[str | None]
    parentId : Mapped[str | None]
    size : Mapped[int | None]
    item_type : Mapped[SysItemType]
    date : Mapped[datetime] #= mapped_column(primary_key=True,  autoincrement=False)

    #__table_args__ = (
    #    PrimaryKeyConstraint(id, date),
    #)

async def create_tables():
    async with aengine.begin() as conn:
        await conn.run_sync(Model.metadata.create_all)

async def delete_tables():
    async with aengine.begin() as conn:
        await conn.run_sync(Model.metadata.drop_all)