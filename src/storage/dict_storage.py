from typing import List

from src.storage.i_storage import (
    IStorage,
    StorageError,
    ObjectNotFoundError,
    StorageTypeUnknownError,
)
from src.dtos import LocationDTO, Store


class DictStorageError(
    StorageError,
):
    """"""


class DictStorage(IStorage):
    """In-memory storage implementation using a dictionary"""

    def __init__(self):
        self._storage = {}

    def _check_storage_type(self, path: LocationDTO) -> None:
        """Check if the storage type is supported"""
        if path.store != Store.DICT:
            raise StorageTypeUnknownError(f"Storage type not supported: {path}")

    def write(self, content: bytes, path: LocationDTO):
        """Stores content in memory under the specified path"""
        self._check_storage_type(path)
        self._storage[path.path] = content

    def read(self, path: LocationDTO) -> bytes:
        """Retrieves content from memory by path"""
        self._check_storage_type(path)
        if path.path not in self._storage:
            raise ObjectNotFoundError(f"Path not found: {path}")
        return self._storage[path.path]

    def list(self, path: LocationDTO) -> list[LocationDTO]:
        """
        Lists all files in given storage location. Only returns files at top level,
        not from subfolders.
        """
        self._check_storage_type(path)
        result = []
        for known_object in self._storage:
            if known_object.startswith(path.path):
                result.append(LocationDTO(known_object))
        return result

    @property
    def supported_storage_types(self) -> List[Store]:
        """Returns supported storage types"""
        return [Store.DICT]
