from fastapi import APIRouter
from disk.schemas import DiskItemsDTO
from disk.repository import DiskItemRepository

router = APIRouter(
    prefix = "/disk",
    tags=['Диск',]
)

@router.post('')
async def insert_diskitems(items : DiskItemsDTO):
    await DiskItemRepository.persist_diskitems(items.items, date=items.updateDate)
    return {"status" : "ok"}