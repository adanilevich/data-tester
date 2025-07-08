from abc import ABC, abstractmethod
from typing import List

class StorageError(Exception):
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
    def read(self, path: str) -> bytes:
        """
        Loads object from specified path (e.g. on local storage) as bytes.
        """

    @abstractmethod
    def write(self, content: bytes, path: str):
        """
        Write bytecontent to speficied path.
        """
