from typing import List

from src.domain_config.ports import (
    IStorage as IDomainConfigStorage,
    StorageError as DomainConfigStorageError,
)
from src.report.ports import (
    IStorage as IReportStorage,
    StorageError as ReportStorageError,
    ObjectNotFoundError as ReportStorageObjectNotFoundError,
    StorageTypeUnknownError as ReportStorageTypeUnknownError,
)
from src.dtos.location import LocationDTO, Store


class DictStorageError(DomainConfigStorageError, ReportStorageError):
    """"""


class ObjectNotFoundError(ReportStorageObjectNotFoundError):
    """"""


class StorageTypeUnknownError(ReportStorageTypeUnknownError):
    """"""


class DictStorage(IDomainConfigStorage, IReportStorage):
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

    def find(self, path: LocationDTO) -> List[LocationDTO]:
        """Returns all files in path, prefixed with the protocol"""
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
