import pytest
from src.storage.dict_storage import (
    DictStorage,
    StorageTypeUnknownError,
    ObjectNotFoundError,
)
from src.dtos.location import LocationDTO, Store


class TestDictStorage:
    @pytest.fixture
    def storage(self) -> DictStorage:
        return DictStorage()

    def test_supported_storage_types(self, storage):
        assert Store.DICT in storage.supported_storage_types
        assert len(storage.supported_storage_types) == 1

    def test_write_and_read(self, storage):
        path = LocationDTO("dict://folder/file.txt")
        content = b"hello world"
        storage.write(content, path)
        # read expects path.path as key
        read_content = storage.read(LocationDTO("dict://folder/file.txt"))
        assert read_content == content

    def test_find_returns_matching_paths(self, storage):
        path1 = LocationDTO("dict://folder/file1.txt")
        path2 = LocationDTO("dict://folder/file2.txt")
        path3 = LocationDTO("dict://other/file3.txt")
        storage.write(b"a", path1)
        storage.write(b"b", path2)
        storage.write(b"c", path3)
        # find should return only those under folder/
        found = storage.find(LocationDTO("dict://folder/"))
        assert path1 in found
        assert path2 in found
        assert path3 not in found

    def test_read_nonexistent_raises(self, storage):
        path = LocationDTO("dict://folder/missing.txt")
        with pytest.raises(ObjectNotFoundError):
            storage.read(path)

    def test_wrong_store_type_raises(self, storage):
        path = LocationDTO("local://folder/file.txt")
        with pytest.raises(StorageTypeUnknownError):
            storage.write(b"x", path)
        with pytest.raises(StorageTypeUnknownError):
            storage.read(path)
        with pytest.raises(StorageTypeUnknownError):
            storage.find(path)
