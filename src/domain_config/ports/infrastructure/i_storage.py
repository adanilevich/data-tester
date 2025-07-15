from abc import ABC, abstractmethod
from typing import List

from src.dtos.location import LocationDTO


class StorageError(Exception):
    """"""

class IStorage(ABC):
    """
    Interface for interaction with storage systems. Methods follow semantics of fsspec.
    All methods must raise StorageError in case of any exceptions
    """

    @abstractmethod
    def find(self, path: LocationDTO) -> List[LocationDTO]:
        """
        Lists all objects stored at location (which are potential domain config objects).
        Returns all specific objects but not containes, e.g. files but not folders.
        """

    @abstractmethod
    def read(self, path: LocationDTO) -> bytes:
        """
        Loads object from specified path (e.g. on local storage) as bytes.
        """

    @abstractmethod
    def write(self, content: bytes, path: LocationDTO):
        """
        Write bytecontent to speficied path.
        """
