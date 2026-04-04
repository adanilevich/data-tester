from abc import ABC, abstractmethod

from src.dtos.storage_dtos import LocationDTO
from src.infrastructure_ports.i_dto_storage import IDtoStorage


class IDtoStorageFactory(ABC):
    """Factory for creating DTO storage instances based on storage location."""

    @abstractmethod
    def get_storage(self, storage_location: LocationDTO) -> IDtoStorage:
        """
        Returns an IDtoStorage implementation for the given storage location.

        Args:
            storage_location: The location that determines the storage backend

        Returns:
            IDtoStorage implementation

        Raises:
            StorageTypeUnknownError: If the storage type is not supported
        """
