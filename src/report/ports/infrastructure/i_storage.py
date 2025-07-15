from abc import ABC, abstractmethod
from typing import List

from src.dtos.location import LocationDTO, Store


class StorageError(Exception):
    """"""

class ObjectNotFoundError(StorageError):
    """"""

class StorageTypeUnknownError(StorageError):
    """
    To be raised when path type is unknown or unsupported, e.g. when passing a database
    location string to a file storage handler.
    """


class IStorage(ABC):
    """
    Abstracts report storage interface -- e.g. stores reports as files to disk.
    """


    @abstractmethod
    def write(self, content: bytes, path: LocationDTO):
        """
        Stores content to disk under speficied path.

        Raises:
            StorageError
        """

    @abstractmethod
    def read(self, path: LocationDTO) -> bytes:
        """
        Loads object from specified path as bytes.
        """

    @property
    @abstractmethod
    def supported_storage_types(self) -> List[Store]:
        """
        Returns a list of supported storage types, e.g. ['local', 'gcs'].
        """

