import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete
from src.database import DiskHistoryItems, DiskFolderOrm

@pytest.fixture(scope='class')
async def clean_db(test_session : AsyncSession):
    yield
    await test_session.execute(delete(DiskFolderOrm))
    await test_session.execute(delete(DiskHistoryItems))
    await test_session.commit()