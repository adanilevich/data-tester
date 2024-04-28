from abc import ABC, abstractmethod
from typing import Any, List


class StorageError(Exception):
    """"""


class StorageContentTypeUnknownError(StorageError):
    """"""


class IStorage(ABC):
    """
    Interface for interaction with storage systems. Methods follow semantics of fsspec.
    All methods must raise StorageError in case of any exceptions
    """

    @abstractmethod
    def find(self, path: str) -> List[str]:
        """
        Lists all objects stored at location (which are potential domain config objects).
        Returns all specific objects but not containes, e.g. files but not folders.
        """

    @abstractmethod
    def read(self, path: str, content_type: str, encoding: str | None = None,) -> Any:
        """
        Loads object as text. enconding, erros, newline follow 'open' semantics.
        """

    @abstractmethod
    def write(self, content: Any, path: str, content_type: str,
              enconding: str | None = None):
        """
        Loads object as bytes.
        """
