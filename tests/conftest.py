import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from src.main import app
from src.disk.router import get_session
from sqlalchemy import event
from src.database import Model
from sqlalchemy.pool import StaticPool
from sqlalchemy import DDL

test_aengine = create_async_engine("sqlite+aiosqlite:///:memory:", poolclass=StaticPool, connect_args={'check_same_thread':False}, echo=True)
session_maker = async_sessionmaker(test_aengine, autoflush=True, expire_on_commit=True)
delete_history_tr = DDL('''\
CREATE TRIGGER IF NOT EXISTS delete_history AFTER DELETE ON disk_folders_table
  BEGIN
    DELETE FROM disk_history WHERE (id = old.id);
  END;''')

@event.listens_for(test_aengine.sync_engine, "connect")
def enable_sqlite_fks(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

@pytest.fixture(scope='class')
async def test_client(test_session : AsyncSession):

    async def get_session_override():  
        return test_session
    
    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()

@pytest.fixture(scope='session', autouse=True)
async def test_db():
    async with test_aengine.begin() as conn:
        await conn.run_sync(Model.metadata.create_all)
        await conn.execute(delete_history_tr)
        yield test_aengine
        async with test_aengine.begin() as conn:
            await conn.execute(DDL("DROP TRIGGER IF EXISTS delete_history;"))
            await conn.run_sync(Model.metadata.drop_all)

@pytest.fixture(scope='class')
async def test_session():
    async with session_maker() as session:
        yield session
        await session.flush()
        await session.rollback()

@pytest.fixture()
def valid_request_data():
    request_data = {
      "items": [
        {
          "id": "элемент_1_4",
          "url": "/file/url1",
          "parentId": None,
          "size": 10,
          "type": "FILE"
        },
        {
          "id": "элемент_1_5",
          "url": None,
          "parentId": None,
          "size": None,
          "type": "FOLDER"
        }
      ],
      "updateDate": "2022-05-28T21:12:01.000Z"
    }
    return request_data

@pytest.fixture()
def valid_file():
    file_data = {
        "id": "элемент_1_4",
        "url": "/file/url1",
        "parentId": None,
        "size": 234,
        "type": "FILE"
    }
    return file_data

@pytest.fixture()
def valid_folder():
    folder_data = {
        "id": "элемент_1_5",
        "url": None,
        "parentId": None,
        "size": None,
        "type": "FOLDER"
    }
    return folder_data