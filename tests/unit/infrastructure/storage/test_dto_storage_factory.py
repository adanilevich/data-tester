import pytest

from src.infrastructure.storage.dto_storage_factory import DtoStorageFactory
from src.infrastructure.storage.dto_storage_file import (
    LocalDtoStorage,
    MemoryDtoStorage,
)
from src.infrastructure_ports import StorageTypeUnknownError
from src.dtos import LocationDTO


class TestDtoStorageFactory:
    @pytest.fixture
    def factory(self) -> DtoStorageFactory:
        return DtoStorageFactory()

    def test_get_storage_memory(self, factory: DtoStorageFactory):
        storage = factory.get_storage(LocationDTO("memory://data/"))
        assert isinstance(storage, MemoryDtoStorage)

    def test_get_storage_local(self, factory: DtoStorageFactory):
        storage = factory.get_storage(LocationDTO("local:///tmp/test_storage/"))
        assert isinstance(storage, LocalDtoStorage)

    def test_get_storage_gcs_without_project_raises(self, factory: DtoStorageFactory):
        with pytest.raises(StorageTypeUnknownError):
            factory.get_storage(LocationDTO("gcs://bucket/"))

    def test_get_storage_unsupported_raises(self, factory: DtoStorageFactory):
        with pytest.raises(StorageTypeUnknownError):
            factory.get_storage(LocationDTO("dict://data/"))
