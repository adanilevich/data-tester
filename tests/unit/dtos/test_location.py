import pytest

from src.dtos.location import LocationDTO, Store


def test_location_dto():
    loc = LocationDTO("local://test")
    assert isinstance(loc, LocationDTO)
    assert loc.path == "local://test/"
    assert loc.store.value == "local"

def test_location_dto_invalid_path():
    with pytest.raises(ValueError):
        LocationDTO("test")

def test_location_dto_store():
    loc = LocationDTO("local://test")
    assert loc.store.value == "local"
    assert loc.store == Store.LOCAL

def test_location_dto_append():
    loc = LocationDTO("local://test")
    new_loc = loc.append("sub")
    assert new_loc.path == "local://test/sub/"
    assert loc.path == "local://test/"

def test_location_dto_filename():
    loc = LocationDTO("local://test/file.txt")
    assert loc.filename == "file.txt"

def test_to_dict():
    loc = LocationDTO("local://test/file.txt")
    assert loc.to_dict() == {"path": "local://test/file.txt"}

def test_to_dict_from_dict():
    loc = LocationDTO("local://test/file.txt")
    assert loc.to_dict() == {"path": "local://test/file.txt"}
    new_loc = LocationDTO.from_dict(loc.to_dict())
    assert loc == new_loc

def test_to_json_from_json():

    loc = LocationDTO("local://test/file.txt")
    loc_as_json = loc.to_json()
    assert loc_as_json == '{"path":"local://test/file.txt"}'

    new_loc = LocationDTO.from_json(loc_as_json)
    assert loc == new_loc

