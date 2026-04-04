from src.infrastructure_ports import (
    IUserStorageFactory,
    IUserStorage,
    StorageTypeUnknownError,
    StorageError
)
from src.dtos.storage_dtos import StorageType
from .user_storage import LocalUserStorage, MemoryUserStorage, GcsUserStorage


class UserStorageFactory(IUserStorageFactory):
    """Factory for creating user storage instances based on storage type."""

    def __init__(self, gcp_project: str | None = None):
        self._gcp_project: str | None = gcp_project
        self._memory_storage: MemoryUserStorage | None = None

    def get_storage(self, storage_type: StorageType) -> IUserStorage:
        match storage_type:
            case StorageType.LOCAL:
                return LocalUserStorage()
            case StorageType.GCS:
                if self._gcp_project is None:
                    raise StorageError("GCS storage requires gcp_project configuration")
                return GcsUserStorage(self._gcp_project)
            case StorageType.MEMORY:
                if self._memory_storage is None:
                    self._memory_storage = MemoryUserStorage()
                return self._memory_storage
            case _:
                raise StorageTypeUnknownError(f"Storage type {storage_type} unsupported")
