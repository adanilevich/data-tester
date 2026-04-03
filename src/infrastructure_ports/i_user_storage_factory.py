from abc import ABC, abstractmethod

from src.dtos.storage import StorageType
from src.infrastructure_ports.i_user_storage import IUserStorage


class IUserStorageFactory(ABC):
    """Factory for creating user storage instances based on storage type."""

    @abstractmethod
    def get_storage(self, storage_type: StorageType) -> IUserStorage:
        """
        Returns an IUserStorage implementation for the given storage type.

        Args:
            storage_type: The type of storage backend to use

        Returns:
            IUserStorage implementation

        Raises:
            StorageTypeUnknownError: If the storage type is not supported
        """
