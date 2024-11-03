import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from copy import copy
from datetime import datetime 

@pytest.mark.usefixtures('load_test_data')
class TestImport:
    @pytest.mark.parametrize(
            'id1,type_1,parentId1,id2,type_2,parentId2,expectation_code', [
            ('newid1','FILE',  None, 'newid2','FILE','newid1',400),
            ('newid1','FOLDER',None, 'newid2','FILE','newid1',200),
            ('newid1','FOLDER',None, 'newid2','FILE','id6',400),
            ('newid1','FOLDER',None, 'newid2','FILE','id1',200),
            ('newid1','FILE', None, 'newid2','FILE','id1',400),
        ]
    )
    def test_insert_diskitems(
        self, test_client : TestClient, valid_request_data : list, valid_file, valid_folder,
        id1, type_1, parentId1, id2, type_2, parentId2, expectation_code,
        ):
        item1 = copy(valid_file) if type_1 == "FILE" else copy(valid_folder)
        item2 = copy(valid_file) if type_2 == "FILE" else copy(valid_folder)
        item1['id'] = id1
        item1['type'] = type_1
        item1['parentId'] = parentId1
        item2['id'] = id2
        item2['type'] = type_2
        item2['parentId'] = parentId2
        valid_request_data['items'] = [item1, item2]
        response = test_client.post(
            url = '/disk/imports',
            json= valid_request_data
            )
        assert response.status_code == expectation_code

@pytest.mark.usefixtures('load_test_data')
class TestDelete:
    @pytest.mark.parametrize(
            'id,expectation_code, ', [
            ('id5',200),
            ('id5',404),
            ('id2',200),
            ('id4',404),
            ('id3',200),
            ('id6',404),
            ('id1',200),
        ]
    )
    def test_delete_endpoint(self, test_client : TestClient, id, expectation_code):
        response = test_client.delete(
            url = f'/disk/delete/{id}',
            params = {'date' : datetime(2024,1,1,1,1,1,1)}
            )
        assert response.status_code == expectation_code  

    def test_delete_invalid_request(self, test_client : TestClient):
        response = test_client.delete(
            url = f'/disk/delete/{id}',
            params = {'date' : "2024-13-12T12:12:12"}
            )
        assert response.status_code == 400

def fill_id_size_set(node_size : set, node : dict) -> None:
    if child_list:=node.get('children', None):
        for child in child_list:
            fill_id_size_set(node_size, child)
    node_size.add((node['id'],node['size']))

@pytest.mark.usefixtures('load_test_data')
class TestNodes:
    @pytest.mark.parametrize(
            'id,expectation_code,size_id_set', [
            ('id5',200,set([('id5',10)])),
            ('id3',200,set([('id3',15),('id6',15)])),
            ('id2',200,set([('id2',15),('id4',5),('id5',10)])),
            ('id1',200,set([('id1',15),('id3',15),('id6',15)])),
            ('randid', 404, set())
        ]
    )
    def test_retreve_endpoint(self, test_client : TestClient, id, expectation_code, size_id_set):
        response = test_client.get(
            url = f'/disk/nodes/{id}'
            )
        assert response.status_code == expectation_code
        json_tree = response.json()
        id_size : set = set()
        if expectation_code != 404:
            fill_id_size_set(id_size, json_tree)
            assert id_size == size_id_set

@pytest.mark.usefixtures('load_test_history_data')
class TestUpdates:
    @pytest.mark.parametrize(
        "datetime,status,result_ids",[
            (f'{datetime(2024,1,2,1,1,1)}',200,set(['id4','id6'])),
            (f'{datetime(2024,1,3,1,1,1)}',200, set(['id6'])),
            (f'{datetime(2024,1,3,1,1,2)}',200, set()),
            (f'{datetime(2024,1,1,22,1,1)}',200, set(['id4'])),
            (f'2022-13-28T21:12:01.000Z',400, set()),
        ]
    )
    def test_update_handler(self, test_client : TestClient, datetime:str ,status, result_ids):
        response = test_client.get(
            url = f'/disk/updates',
            params = {'date' : datetime}
        )
        assert response.status_code == status
        response_dict = response.json()
        item_ids = set()
        if response.status_code != 400:
            for item in response_dict['items']:
                item_ids.add(item['id'])
            assert item_ids == result_ids
            assert len(response_dict['items']) == len(result_ids)

@pytest.mark.usefixtures('load_test_history_data')
class TestHistory:
    @pytest.mark.parametrize(
        "id,datetime_start,datetime_end,status,items_length",[
            ('id4',f'{datetime(2024,1,1,2,1,1)}',f'{datetime(2024,1,1,22,1,2)}',200,2),
            ('id1',f'{datetime(2024,1,1,1,1,1)}',f'{datetime(2024,1,2,1,1,1)}',200,1),
            ('id1',f'{datetime(2010,1,1,2,1,1)}',f'{datetime(2024,1,2,1,1,2)}',200,2),
            ('id1',f'{datetime(2024,1,1,1,1,2)}',f'{datetime(2024,1,2,1,1,1)}',404,0),
            ('id1',f'{datetime(2025,1,1,22,1,1)}',f'{datetime(2024,1,1,2,1,1)}',400,0),
            ('id1',f'{datetime(2024,1,1,2,1,1)}',f'2025-13-28T21:12:01.000Z',400,0),
            ('randid',f'{datetime(2010,1,1,2,1,1)}',f'{datetime(2025,1,1,22,1,1)}',404,0),
        ]
    )
    def test_history_handler(self, test_client : TestClient, id, datetime_start, datetime_end, status, items_length):
        response = test_client.get(
            url = f'/disk/node/{id}/history',
            params = {'dateStart' : datetime_start, 'dateEnd' : datetime_end}
        )
        assert response.status_code == status
        data = response.json()
        if response.status_code == 200:
            for item in data['items']:
                assert item['id'] == id
            assert len(data['items']) == items_length