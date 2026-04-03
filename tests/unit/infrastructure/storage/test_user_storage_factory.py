import pytest

from src.infrastructure.storage.user_storage_factory import UserStorageFactory
from src.infrastructure.storage.user_storage import (
    LocalUserStorage,
    MemoryUserStorage,
)
from src.infrastructure_ports import StorageTypeUnknownError, StorageError
from src.dtos import StorageType


class TestUserStorageFactory:
    @pytest.fixture
    def factory(self) -> UserStorageFactory:
        return UserStorageFactory()

    def test_get_storage_local(self, factory: UserStorageFactory):
        storage = factory.get_storage(StorageType.LOCAL)
        assert isinstance(storage, LocalUserStorage)

    def test_get_storage_memory(self, factory: UserStorageFactory):
        storage = factory.get_storage(StorageType.MEMORY)
        assert isinstance(storage, MemoryUserStorage)

    def test_get_storage_memory_singleton(self, factory: UserStorageFactory):
        s1 = factory.get_storage(StorageType.MEMORY)
        s2 = factory.get_storage(StorageType.MEMORY)
        assert s1 is s2

    def test_get_storage_local_not_singleton(self, factory: UserStorageFactory):
        s1 = factory.get_storage(StorageType.LOCAL)
        s2 = factory.get_storage(StorageType.LOCAL)
        assert s1 is not s2

    def test_get_storage_unsupported_raises(self, factory: UserStorageFactory):
        with pytest.raises(StorageTypeUnknownError):
            factory.get_storage(StorageType.UNSUPPORTED)

    def test_get_storage_gcs_without_project_raises(self, factory: UserStorageFactory):
        with pytest.raises(StorageError):
            factory.get_storage(StorageType.GCS)
