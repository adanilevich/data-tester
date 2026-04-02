from .i_formatter_factory import IFormatterFactory
from .i_formatter import IFormatter
from .json_formatter import JsonFormatter
from src.dtos.location import ObjectType


class StorageFormatterFactoryError(Exception):
    """
    Exception raised when a storage formatter factory operation fails.
    """


class UnknownStorageObjectTypeError(StorageFormatterFactoryError):
    """
    Exception raised when an unknown storage object is requested.
    """


class FormatterFactory(IFormatterFactory):
    """Factory for creating formatter implementations."""

    def __init__(self):
        self._json_formatter = JsonFormatter()

    def get_formatter(self, object_type: ObjectType) -> IFormatter:
        """
        Get the appropriate formatter for the given object type.
        Currently all objects use JSON formatting.
        """
        if object_type == ObjectType.UNKNOWN:
            raise UnknownStorageObjectTypeError(
                "Cannot get formatter for unknown object type"
            )

        return self._json_formatter
