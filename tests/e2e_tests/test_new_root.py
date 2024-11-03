import pytest
from fastapi.testclient import TestClient
import json
from .valid_results import get_node_4string, get_node_4string_final, updates_no_deletes, get_string4_post_deletes, updates_post_deletes, string4_history

@pytest.fixture()
def first_insert_json():
    data = {
        "items": [
          {
            "id": "string",
            "url": "string",
            "parentId": "string2",
            "type": "FILE",
            "size": 6
          },
          {
            "id": "string1",
            "url": "string1",
            "parentId": "string2",
            "type": "FILE",
            "size": 5
          },
          {
            "id": "string2",
            "url": None,
            "parentId": None,
            "type": "FOLDER",
            "size": None
          },
          {
            "id": "string3",
            "url": None,
            "parentId": None,
            "type": "FOLDER",
            "size": None
          }
        ],
        "updateDate": "2024-11-02T04:25:26.896Z"
    }
    data = json.dumps(data)
    return data

@pytest.fixture()
def second_insert_json():
    data = {
        "items": [
          {
            "id": "string1",
            "url": "string1",
            "parentId": "string3",
            "type": "FILE",
            "size": 6
          },
          {
            "id": "string2",
            "url": None,
            "parentId": "string4",
            "type": "FOLDER",
            "size": None
          },
          {
            "id": "string4",
            "url": None,
            "parentId": None,
            "type": "FOLDER",
            "size": None
          }
        ],
        "updateDate": "2024-11-02T05:25:26.896Z"
    }
    data = json.dumps(data)
    return data

@pytest.fixture()
def third_insert_json():
    data = {
        "items": [
          {
            "id": "string5",
            "url": "string1",
            "parentId": "string4",
            "type": "FILE",
            "size": 10
          },
          {
            "id": "string1",
            "url": "string1",
            "parentId": None,
            "type": "FILE",
            "size": 10
          },
          {
            "id": "string3",
            "url": None,
            "parentId": "string4",
            "type": "FOLDER",
            "size": None
          }
        ],
        "updateDate": "2024-11-02T06:25:26.896Z"
    }
    data = json.dumps(data)
    return data

def shallow_compare(item1 : dict , item2 : dict) -> bool:
    assert item1['id'] == item2['id']
    assert item1['url'] == item2['url']
    assert item1['date'] == item2['date']
    assert item1['parentId'] == item2['parentId']
    assert item1['type'] == item2['type']
    assert item1['size'] == item2['size']
    return True

def deep_compare(item1 : dict , item2 : dict) -> bool:
    shallow_compare(item1, item2)
    ch1 : list = item1['children']
    ch2 : list = item2['children']
    if ch1 == None and ch2 == None:
        return True
    elif ch1 == None or ch1 == None:
       return False
    assert len(ch1) == len(ch2)
    ch1.sort(key=lambda x : x['id'])
    ch2.sort(key=lambda x : x['id'])
    for child1, child2 in zip(ch1,ch2):
        deep_compare(child1, child2)
    return True

@pytest.mark.usefixtures('clean_db')
class TestEdgeCases:
    '''
      End to end test scenario
    '''
    def test_insert_new_root(self, test_client: TestClient, first_insert_json, second_insert_json):
        response = test_client.post(
            url='/disk/imports',
            content = first_insert_json,
        )
        assert response.status_code == 200
        response = test_client.post(
            url='/disk/imports',
            content = second_insert_json,
        )
        assert response.status_code == 200
        
        response = test_client.get(
            url = f'/disk/nodes/string4',
        )
        assert response.status_code == 200
        data = response.json()
        assert deep_compare(data, get_node_4string)

    def test_update_and_folder_switch(self, test_client: TestClient, third_insert_json):
        response = test_client.post(
            url='/disk/imports',
            content = third_insert_json,
        )
        assert response.status_code == 200
        response = test_client.get(
            url = f'/disk/nodes/string4',
        )
        assert response.status_code == 200
        data = response.json()
        assert deep_compare(data, get_node_4string_final)
        response = test_client.get(
            url = '/disk/updates',
            params={'date' : "2024-11-02T06:25:26.896Z"}
        )
        assert response.status_code == 200
        data = response.json()
        data['items'].sort(key=lambda x : x['id'])
        updates_no_deletes['items'].sort(key=lambda x : x['id'])
        for item1, item2 in zip(data['items'], updates_no_deletes['items']):
            assert shallow_compare(item1, item2)

    def test_file_and_folder_deletion(self, test_client: TestClient):
        response = test_client.delete(
            url = '/disk/delete/string2',
            params={'date' : "2024-11-02T07:25:26.896Z"}
        )
        assert response.status_code == 200
        response = test_client.delete(
            url = '/disk/delete/string5',
            params={'date' : "2024-11-02T08:25:26.896Z"}
        )
        assert response.status_code == 200
        response = test_client.get(
            url = f'/disk/nodes/string4',
        )
        assert response.status_code == 200
        data = response.json()
        assert deep_compare(data, get_string4_post_deletes)
        response = test_client.get(
            url = '/disk/updates',
            params={'date' : "2024-11-02T08:25:26.896Z"}
        )
        assert response.status_code == 200
        data = response.json()
        data['items'].sort(key=lambda x : x['id'])
        updates_post_deletes['items'].sort(key=lambda x : x['id'])
        for item1, item2 in zip(data['items'], updates_post_deletes['items']):
            assert shallow_compare(item1, item2)

    def test_history_after_deletion_updates_inserts(self, test_client: TestClient):
        response = test_client.get(
            url = '/disk/node/string4/history',
            params={'dateStart': "2024-11-02T01:25:26.896Z", 'dateEnd' : "2024-11-02T09:25:26.896Z"}
        )
        assert response.status_code == 200
        data = response.json()
        data['items'].sort(key=lambda x : x['date'])
        string4_history['items'].sort(key=lambda x : x['date'])
        for item1, item2 in zip(data['items'], string4_history['items']):
            assert shallow_compare(item1, item2)