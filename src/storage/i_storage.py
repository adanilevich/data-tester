from abc import ABC, abstractmethod
from typing import List
from src.dtos.location import LocationDTO, Store


class StorageError(Exception):
    """Base exception for storage errors."""


class ObjectNotFoundError(StorageError):
    """Raised when an object is not found in storage."""


class StorageTypeUnknownError(StorageError):
    """Raised when the storage type is unknown or unsupported."""


class IStorage(ABC):
    """
    Abstracts storage interface -- e.g. stores objects as files to disk.
    """
    @abstractmethod
    def write(self, content: bytes, path: LocationDTO):
        """
        Stores content to disk under specified path.
        Raises:
            StorageError
        """

    @abstractmethod
    def read(self, path: LocationDTO) -> bytes:
        """
        Loads object from specified path as bytes.
        """

    @abstractmethod
    def list(self, path: LocationDTO) -> list[LocationDTO]:
        """
        Lists all files in given storage location. Only returns files at top level,
        not from subfolders.
        """

    @property
    @abstractmethod
    def supported_storage_types(self) -> List[Store]:
        """
        Returns a list of supported storage types, e.g. ['local', 'gcs'].
        """
