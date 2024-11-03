from fastapi import APIRouter, Response, Query, status, Depends
from sqlalchemy.ext.asyncio  import AsyncSession
from typing import Annotated, AsyncIterator
from datetime import datetime
from .exceptions import DiskItemException
from .schemas import DiskItemsDTO,DiskItemRetreweSchema, HistoryResponse
from .exceptions import Error
from .service import DiskItemService
from src.database import new_session


router_responses = {
    400: {
        "description": "Invalid document schema or invalid input data",
        "model" : Error,
        "content" : {
            "application/json": {
                "example": {"code": 400, "message": "Validation Failed"}
            }
        }
    },
    404: {
        "description": "Items not found",
        "model" : Error,
        "content" : {
            "application/json": {
                "example": {"code": 404, "message": "Items not found"}
            }
        }
    },
    422 : {
        "description": "Returns code 400 instead",
        "model" : Error,
        "content" : {
            "application/json": {
                "example": {"code": 400, "message": "Validation Failed"}
            }
        }
    }
}

async def get_session() -> AsyncIterator[AsyncSession]:
    async with new_session() as session:
        yield session

router = APIRouter(
    prefix = "/disk",
    tags=['Диск',],
    responses= {422 : router_responses[422]}
)

@router.post(
    '/imports',
    description="""Imports disk items elements. Importing existing elements updates them.
    It is guaranteed that there are no cyclic dependencies in the input data and the UpdateDate field increases monotonously. 
    It is guaranteed that when checking, the transmitted time is a multiple of seconds.""",
    response_description="Successful import",
    status_code=status.HTTP_200_OK,
    responses = {400 : router_responses[400]},
)
async def insert_diskitems(session : Annotated[AsyncSession, Depends(get_session)], items : DiskItemsDTO | None = None) -> Response:
    if items != None:
        await DiskItemService.persist_diskitems(items.items, date=items.updateDate, session=session)
    await session.commit()
    return Response(status_code=200)

@router.delete('/delete/{id}',        
    description="Delete element information by id",
    response_description="Successeful deletion",
    status_code=status.HTTP_200_OK,
    responses = {400 : router_responses[400], 404: router_responses[404]},
)
async def delete_diskitem(session : Annotated[AsyncSession, Depends(get_session)], id : str, date : datetime) -> Response:
    await DiskItemService.delete_item(id, date, session)
    await session.commit()
    return Response(status_code=200)

@router.get('/nodes/{id}',         
    description="Get information by id",
    response_description="Information about element",
    status_code=status.HTTP_200_OK,
    responses = {404: router_responses[404]},
)
async def get_diskitem(session : Annotated[AsyncSession, Depends(get_session)], id : str) -> DiskItemRetreweSchema:
    diskitem = await DiskItemService.get_item(id, session)
    await session.commit()
    return diskitem

@router.get('/updates',         
    status_code=200,
    response_description="Updated elemenents list",
    description="Getting files that have been updated in the last 24 hours inclusive [date - 24h, date]",
    responses = {400 : router_responses[400]},
)
async def get_updates(session : Annotated[AsyncSession, Depends(get_session)], date : Annotated[datetime, Query()]) -> HistoryResponse:
    updates = await DiskItemService.get_update_24h(date, session)
    await session.commit()
    return updates

@router.get('/node/{id}/history',         
    status_code=200,
    response_description="Element history",
    description="Getting the update history for an element for a given half-interval [from, to)",
    responses = {400 : router_responses[400], 404: router_responses[404]},
)
async def get_history(session : Annotated[AsyncSession, Depends(get_session)], id : str, dateStart : datetime, dateEnd : datetime) -> HistoryResponse:
    if dateStart >= dateEnd:
        raise DiskItemException(status_code=400)
    history = await DiskItemService.get_history(id, dateStart, dateEnd, session)
    await session.commit()
    return history