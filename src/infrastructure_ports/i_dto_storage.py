from abc import ABC, abstractmethod
from typing import Dict, List

from src.dtos.dto import DTO
from src.dtos.storage_dtos import ObjectType


class IDtoStorage(ABC):
    """
    Interface for internal DTO persistence. Storage location is fixed at
    construction time. Subfolder organization is handled internally by the
    implementation. ObjectType is inferred from the DTO class in write_dto.
    """

    @abstractmethod
    def read_dto(self, object_type: ObjectType, id: str) -> DTO:
        """
        Reads and deserializes a DTO by its type and ID.

        Args:
            object_type: Type of object to retrieve
            id: Identifier for the specific object

        Returns:
            Deserialized DTO object

        Raises:
            ObjectNotFoundError: If object is not found
            StorageError: For other storage errors
        """

    @abstractmethod
    def write_dto(self, dto: DTO) -> None:
        """
        Serializes and writes a DTO. The implementation determines the
        ObjectType and storage path from the DTO's class and attributes.

        Args:
            dto: The DTO object to store

        Raises:
            StorageError: For storage errors
        """

    @abstractmethod
    def delete_dto(self, object_type: ObjectType, id: str) -> None:
        """
        Deletes a DTO by its type and ID.

        Raises:
            ObjectNotFoundError: If object is not found
            StorageError: For other storage errors
        """

    @abstractmethod
    def list_dtos(
        self,
        object_type: ObjectType,
        filters: Dict[str, str] | None = None,
        order_by: str | None = None,
    ) -> List[DTO]:
        """
        Lists DTOs of a given type, optionally filtered and ordered.

        Supported filters: domain, date (YYYY-MM-DD), testrun_id.
        Supported order_by: "date" only (raises ValueError otherwise).

        Args:
            object_type: Type of objects to list
            filters: Optional dict of filter criteria
            order_by: Optional ordering field

        Returns:
            List of deserialized DTO objects

        Raises:
            StorageError: For storage errors
            ValueError: If order_by is not supported
        """
