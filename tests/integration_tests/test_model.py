import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import DiskFolderOrm


@pytest.mark.usefixtures('load_test_data')
class TestDiskFolderOrm:
    @pytest.mark.parametrize(
            'idlist,expectation', [
                (['id5','id6'], ['id1','id3','id2','id5','id6']),
                (['id4', 'id5'], ['id4', 'id5', 'id2']),
                (['id3'], ['id3','id1']),
                (['id2'], ['id2']),
                ([None], []),
                ([],[])
            ]
        )
    async def test_load_ancestors(self, test_session : AsyncSession, idlist, expectation):
        objs = await DiskFolderOrm.load_ancestors(set(idlist), test_session)
        assert set([obj.id for obj in objs]) == set(expectation)