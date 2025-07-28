from abc import ABC, abstractmethod
from .i_formatter import IFormatter
from src.dtos.location import StorageObject


class IFormatterFactory(ABC):
    """Interface for formatter factory implementations."""

    @abstractmethod
    def get_formatter(self, object_type: StorageObject) -> IFormatter:
        """
        Get the appropriate formatter for the given object type.

        Args:
            object_type: Type of object to get formatter for

        Returns:
            Formatter instance for the object type

        Raises:
            ValueError: If object type is not supported
        """
