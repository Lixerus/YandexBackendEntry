import pytest
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import DiskFolderOrm, DiskHistoryItems
from datetime import datetime


@pytest.fixture(scope='class')
async def load_test_data(test_session : AsyncSession):
    obj1 = DiskFolderOrm(id = 'id1', item_type = 'FOLDER', url = None, size= 15, parentId = None, date = datetime(2024,1,1,1,1,1))
    obj2 = DiskFolderOrm(id = 'id2', item_type = 'FOLDER', url = None, size= 15, parentId = None , date = datetime(2024,1,1,1,1,1))
    obj3 = DiskFolderOrm(id = 'id3', item_type = 'FOLDER', url = None, size= 15, parentId = 'id1' , parent = obj1, date = datetime(2024,1,1,1,1,1))
    obj4 = DiskFolderOrm(id = 'id4', item_type = 'FILE', url = 'url1/4', size= 5, parentId = 'id2', parent = obj2, date = datetime(2024,1,1,1,1,1))
    obj5 = DiskFolderOrm(id = 'id5', item_type = 'FILE', url = 'url2/4', size= 10, parentId = 'id2', parent = obj2, date = datetime(2024,1,1,1,1,1))
    obj6 = DiskFolderOrm(id = 'id6', item_type = 'FILE', url = 'url3/2', size= 15, parentId = 'id3', parent = obj3, date = datetime(2024,1,1,1,1,1))
    test_session.add_all([obj1, obj2, obj3, obj4, obj5, obj6])
    await test_session.commit()
    await test_session.close()
    yield
    await test_session.execute(delete(DiskFolderOrm))
    await test_session.commit()

@pytest.fixture(scope='class')
async def load_test_history_data(test_session : AsyncSession):
    obj1 = DiskHistoryItems(id = 'id1', item_type = 'FOLDER', url = None, size= 15, parentId = None, date = datetime(2024,1,1,1,1,1))
    obj2 = DiskHistoryItems(id = 'id2', item_type = 'FOLDER', url = None, size= 10, parentId = None , date = datetime(2024,1,1,22,1,1))
    obj3 = DiskHistoryItems(id = 'id1', item_type = 'FOLDER', url = None, size= 15, parentId = None , date = datetime(2024,1,2,1,1,1))
    obj4 = DiskHistoryItems(id = 'id4', item_type = 'FILE', url = 'url1/4', size= 5, parentId = 'id2', date = datetime(2024,1,1,2,1,1))
    obj5 = DiskHistoryItems(id = 'id4', item_type = 'FILE', url = 'url2/4', size= 10, parentId = 'id2', date = datetime(2024,1,1,22,1,1))
    obj6 = DiskHistoryItems(id = 'id6', item_type = 'FILE', url = 'url3/2', size= 15, parentId = 'id1',  date = datetime(2024,1,2,1,1,1))
    test_session.add_all([obj1, obj2, obj3, obj4, obj5, obj6])
    await test_session.commit()
    await test_session.close()
    yield
    await test_session.execute(delete(DiskHistoryItems))
    await test_session.commit()
