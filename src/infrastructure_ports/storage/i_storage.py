from abc import ABC, abstractmethod
from typing import List
from src.dtos import LocationDTO, Store, StorageObject, ObjectLocationDTO, DTO


class StorageError(Exception):
    """Base exception for storage errors."""


class ObjectNotFoundError(StorageError):
    """Raised when an object is not found in storage."""


class StorageTypeUnknownError(StorageError):
    """Raised when the storage type is unknown or unsupported."""


class IStorage(ABC):
    """
    Abstracts storage interface for structured object storage with serialization.
    """

    @abstractmethod
    def write(self, dto: DTO, object_type: StorageObject, location: LocationDTO):
        """
        Stores a DTO object to (application-internal) storage, serialized according
        to internal format which is handled by the specific storage implementation.
        The implementation handles naming conventions and serialization.

        Args:
            dto: The DTO object to store
            object_type: Type of object being stored
            location: Base location for storage

        Raises:
            StorageError
        """

    @abstractmethod
    def read(
        self, object_type: StorageObject, object_id: str, location: LocationDTO
    ) -> DTO:
        """
        Retrieves and deserializes a DTO object from storage. Implementation must handle
        naming conventions and serialization.

        Args:
            object_type: Type of object to retrieve
            object_id: Identifier for the specific object
            location: Base location to search

        Returns:
            Deserialized DTO object

        Raises:
            ObjectNotFoundError: If object is not found
            StorageError: For other storage errors
        """

    @abstractmethod
    def write_bytes(self, content: bytes, location: LocationDTO):
        """
        Stores raw bytes content to the specified location. This should only be used for
        storing user-facing artifacts in user-managed storage where serialization and
        naming conventions are handled by the clients of the specific implementation of
        IStorage.

        Args:
            content: Raw bytes to store
            location: Exact location including filename

        Raises:
            StorageError
        """

    @abstractmethod
    def read_bytes(self, location: LocationDTO) -> bytes:
        """
        Reads raw bytes content from the specified location. This should only be used for
        reading user-facing artifacts from user-managed storage where serialization and
        naming conventions are handled by the clients of the specific implementation of
        IStorage.

        Args:
            location: Exact location including filename

        Returns:
            Raw bytes content

        Raises:
            ObjectNotFoundError: If object is not found
            StorageError: For other storage errors
        """

    @abstractmethod
    def list(
        self, location: LocationDTO, object_type: StorageObject
    ) -> List[ObjectLocationDTO]:
        """
        Lists all objects of the specified type in the given location. This is meant for
        listing objects from application-internal storage. Implementation must handle
        naming conventions and serialization.

        Args:
            location: Base location to search
            object_type: Type of objects to list

        Returns:
            List of ObjectLocationDTO objects containing object_id and location
        """

    @abstractmethod
    def list_files(self, location: LocationDTO) -> List[LocationDTO]:
        """
        Lists all files in the given location regardless of type. This is meant for
        listing user-managed files like specifications. Client must be able to handle
        the naming conventaions of the locations and paths which are returned.

        Args:
            location: Base location to search

        Returns:
            List of LocationDTO objects for all files found
        """

    @property
    @abstractmethod
    def supported_storage_types(self) -> List[Store]:
        """
        Returns a list of supported storage types, e.g. ['local', 'gcs'].
        """
