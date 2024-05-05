from abc import ABC, abstractmethod
from typing import Any


class StorageError(Exception):
    """"""


class IStorage(ABC):
    """
    Abstracts report storage interface -- e.g. stores reports as files to disk.
    """

    @abstractmethod
    def write(
        self, content: Any, path: str, content_type: str, enconding: str | None = None
    ):
        """
        Stores content (typicall bytes or string) to disk. How data is stored is defined
        by the provided content_type. Implementations must know and be able to handle
        requested content_types (see IReportFormatter)

        Raises:
            StorageError
        """

    @abstractmethod
    def read(self, path: str, content_type: str, encoding: str | None = None,) -> Any:
        """
        Loads object as text. enconding, erros, newline follow 'open' semantics.
        """
