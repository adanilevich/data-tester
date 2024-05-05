from abc import ABC, abstractmethod


class StorageError(Exception):
    """"""


class IStorage(ABC):
    """
    Abstracts report storage interface -- e.g. stores reports as files to disk.
    """

    @abstractmethod
    def write(self, content: bytes, path: str):
        """
        Stores content to disk under speficied path.

        Raises:
            StorageError
        """

    @abstractmethod
    def read(self, path: str) -> bytes:
        """
        Loads object from specified path as bytes.
        """
