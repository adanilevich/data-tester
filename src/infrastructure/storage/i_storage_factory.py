from abc import ABC, abstractmethod
from .i_storage import IStorage
from src.dtos.location import LocationDTO


class IStorageFactory(ABC):
    """Interface for storage factory implementations."""

    @abstractmethod
    def get_storage(self, location: LocationDTO) -> IStorage:
        """
        Creates and returns an appropriate storage implementation based on the
        location type.

        Args:
            location: LocationDTO containing the storage type information

        Returns:
            IStorage: Storage implementation matching the location type

        Raises:
            StorageTypeUnknownError: If the location type is not supported
        """
