import pytest

@pytest.fixture()
def item_on_type(request, valid_file, valid_folder):
    if request.param == "FILE":
        return valid_file
    elif request.param == "FOLDER":
        return valid_folder