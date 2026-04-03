from abc import ABC, abstractmethod
from typing import List

from src.dtos.storage import LocationDTO


class IUserStorage(ABC):
    """
    Interface for reading from user-managed storage (specifications, user artifacts).
    Operates on raw bytes with explicit LocationDTO for every call, since the user
    controls the locations. This is a read-only interface — users manage their own files.
    """

    @abstractmethod
    def read_object(self, location: LocationDTO) -> bytes:
        """
        Reads raw bytes from a user-managed location.

        Args:
            location: Exact location including filename

        Returns:
            Raw bytes content

        Raises:
            ObjectNotFoundError: If object is not found
            StorageError: For other storage errors
        """

    @abstractmethod
    def list_objects(self, location: LocationDTO) -> List[LocationDTO]:
        """
        Lists all files in a user-managed location.

        Args:
            location: Base location to search

        Returns:
            List of LocationDTO objects for all files found
        """
