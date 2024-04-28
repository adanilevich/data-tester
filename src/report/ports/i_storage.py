from abc import ABC, abstractmethod
from typing import Any


class StorageError(Exception):
    """"""


class IStorage(ABC):

    @abstractmethod
    def write(self, content: Any, path: str, content_type: str,
              enconding: str | None = None):
        """
        Loads object as bytes.

        Raises:
            StorageError
        """
