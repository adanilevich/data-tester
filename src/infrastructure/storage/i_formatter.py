from abc import ABC, abstractmethod
from src.dtos.dto import DTO
from src.dtos.location import StorageObject


class FormatterError(Exception):
    """"""


class DeserializationError(FormatterError):
    """"""


class SerializationError(FormatterError):
    """"""


class IFormatter(ABC):
    """Interface for serializing and deserializing DTO objects."""

    @abstractmethod
    def serialize(self, dto: DTO) -> bytes:
        """
        Serialize a DTO object to bytes.

        Args:
            dto: The DTO object to serialize

        Returns:
            Serialized bytes representation
        """

    @abstractmethod
    def deserialize(self, data: bytes, object_type: StorageObject) -> DTO:
        """
        Deserialize bytes back to a DTO object.

        Args:
            data: Serialized bytes data
            object_type: Type of object to deserialize to

        Returns:
            Deserialized DTO object
        """

    @abstractmethod
    def get_object_key(self, object_id: str, object_type: StorageObject) -> str:
        """
        Get the key/filename for storing an object.

        Args:
            object_id: Identifier for the object
            object_type: Type of the object being stored

        Returns:
            Key or filename for storage
        """

    @abstractmethod
    def check_filename(self, filename: str, object_type: StorageObject) -> bool:
        """
        Check if a filename corresponds to the naming convention for given object type.

        Args:
            filename: The filename to check
            object_type: Type of object to check against

        Returns:
            True if filename matches the naming convention
        """

    @abstractmethod
    def get_object_id(self, object_key: str, object_type: StorageObject) -> str:
        """
        Extract object ID from object key based on naming convention.

        Args:
            object_key: The object key/filename to extract from
            object_type: Type of object

        Returns:
            Object ID extracted from the key

        Raises:
            ValueError: If object ID cannot be extracted from the key
        """
