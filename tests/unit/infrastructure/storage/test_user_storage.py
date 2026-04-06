import pytest

from src.infrastructure.storage.user_storage import (
    MemoryUserStorage,
    LocalUserStorage,
)
from src.infrastructure_ports import ObjectNotFoundError, StorageTypeUnknownError
from src.dtos import LocationDTO


class TestMemoryUserStorage:
    @pytest.fixture
    def storage(self) -> MemoryUserStorage:
        from typing import cast
        from fsspec.implementations.memory import MemoryFileSystem

        s = MemoryUserStorage()
        cast(MemoryFileSystem, s.fs).store.clear()
        return s

    def test_read_object_not_found_raises(self, storage: MemoryUserStorage):
        location = LocationDTO("memory://nonexistent.json")
        with pytest.raises(ObjectNotFoundError):
            storage.read_object(location)

    def test_read_object_roundtrip(self, storage: MemoryUserStorage):
        location = LocationDTO("memory://specs/test.json")
        content = b'{"key": "value"}'
        # Write directly via fsspec for test setup
        with storage.fs.open(location.path, mode="wb") as f:
            f.write(content)

        result = storage.read_object(location)
        assert result == content

    def test_list_objects_empty(self, storage: MemoryUserStorage):
        location = LocationDTO("memory://empty_dir/")
        # Create directory by writing and deleting, or just check empty
        with storage.fs.open("empty_dir/placeholder.txt", mode="wb") as f:
            f.write(b"x")
        storage.fs.rm("empty_dir/placeholder.txt")

        # Empty dir may not exist in memory fs after removal
        with pytest.raises(ObjectNotFoundError):
            storage.list_objects(location)

    def test_list_objects_returns_files(self, storage: MemoryUserStorage):
        # Pre-populate files
        with storage.fs.open("specs/schema.json", mode="wb") as f:
            f.write(b'{"schema": true}')
        with storage.fs.open("specs/rowcount.sql", mode="wb") as f:
            f.write(b"SELECT COUNT(*)")

        location = LocationDTO("memory://specs/")
        result = storage.list_objects(location)

        assert len(result) == 2
        filenames = {loc.filename for loc in result}
        assert filenames == {"schema.json", "rowcount.sql"}

    def test_list_objects_single_file(self, storage: MemoryUserStorage):
        with storage.fs.open("specs/schema.json", mode="wb") as f:
            f.write(b'{"schema": true}')

        location = LocationDTO("memory://specs/schema.json")
        result = storage.list_objects(location)

        assert len(result) == 1
        assert result[0].filename == "schema.json"

    def test_list_objects_excludes_subfolders(self, storage: MemoryUserStorage):
        with storage.fs.open("specs/top.json", mode="wb") as f:
            f.write(b"{}")
        with storage.fs.open("specs/sub/nested.json", mode="wb") as f:
            f.write(b"{}")

        location = LocationDTO("memory://specs/")
        result = storage.list_objects(location)

        assert len(result) == 1
        assert result[0].filename == "top.json"

    def test_wrong_storage_type_raises(self, storage: MemoryUserStorage):
        location = LocationDTO("local://some/path/")
        with pytest.raises(StorageTypeUnknownError):
            storage.read_object(location)
        with pytest.raises(StorageTypeUnknownError):
            storage.list_objects(location)


class TestLocalUserStorage:
    def test_creates_instance(self):
        storage = LocalUserStorage()
        assert storage.storage_type.value == "local"
