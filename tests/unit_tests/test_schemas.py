import pytest
from src.disk.schemas import DiskItemImportSchema, DiskItemsDTO
from contextlib import nullcontext
from datetime import datetime
from pydantic import ValidationError


class TestImportSchema:
    @pytest.mark.parametrize(
        'id1,id2,expectation', [
            ('sameid', 'sameid', pytest.raises(ValidationError)),
            ('diffid1', 'diffid2', nullcontext())
        ]
    )
    def test_unique_id(self, valid_request_data : dict[str, list | str], id1, id2, expectation):
        items : list[dict] = valid_request_data['items']
        items[0]['id'] = id1
        items[1]['id'] = id2
        with expectation as exp:
            assert DiskItemsDTO(**valid_request_data)

    @pytest.mark.parametrize(
        'id1,expectation', [
            (None, pytest.raises(ValidationError)),
            ('diffid1', nullcontext())
        ]
    )
    def test_not_null_id(self, valid_file, id1, expectation):
        valid_file['id'] = id1
        with expectation as exp:
            assert DiskItemImportSchema(**valid_file)


    @pytest.mark.parametrize(
        'item_on_type,expectation', [
            ('FILE', pytest.raises(ValidationError)),
            ('FOLDER', nullcontext())
        ], indirect=['item_on_type']
    )
    def test_parent_type(self, valid_request_data, item_on_type, expectation):
        items : list[dict] = valid_request_data['items']
        item_on_type['id'] = 'randomid'
        items[0]['parentId'] = item_on_type['id']
        items.append(item_on_type)
        with expectation as exp:
            assert DiskItemsDTO(**valid_request_data)

    @pytest.mark.parametrize(
        'url,expectation', [
            ("normal/url", nullcontext()),
            (f"{''.join(['u']*255)}", nullcontext()),
            (f"{''.join(['u']*256)}", pytest.raises(ValidationError)),
            (None, pytest.raises(ValidationError))
        ], indirect=False
    )
    def test_file_url(self, valid_file, url, expectation):
        valid_file['url'] = url
        with expectation as exp:
            assert DiskItemImportSchema(**valid_file)

    @pytest.mark.parametrize(
        'size,expectation', [
            (1, nullcontext()),
            (0, pytest.raises(ValidationError)),
            (-1, pytest.raises(ValidationError)),
            (None, pytest.raises(ValidationError))
        ], indirect=False
    )
    def test_file_size(self, valid_file, size, expectation):
        valid_file['size'] = size
        with expectation as exp:
            assert DiskItemImportSchema(**valid_file)


    @pytest.mark.parametrize(
        'timedate,expectation', [
            (datetime(2024,11,1,12,3,4), nullcontext()),
            ("2022-05-28T21:12:01.000Z",nullcontext()),
            ("2022-13-28T21:12:01.000Z", pytest.raises(ValidationError)),
            ("2022-13-28", pytest.raises(ValidationError))
        ], indirect=False
    )
    def test_dateformat(self, valid_request_data, timedate, expectation):
        valid_request_data['updateDate'] = timedate
        with expectation as exp:
            assert DiskItemsDTO(**valid_request_data)

    @pytest.mark.parametrize(
        'size,url,expectation', [
            (0, None,pytest.raises(ValidationError)),
            (None, 'url', pytest.raises(ValidationError)),
            (None, None, nullcontext())
        ], indirect=False
    )
    def test_folder_size_url(self, valid_folder, size, url,expectation ):
        valid_folder['url'] = url
        valid_folder['size'] = size
        with expectation as exp:
            assert DiskItemImportSchema(**valid_folder)