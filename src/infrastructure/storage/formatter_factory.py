from .i_formatter_factory import IFormatterFactory
from .i_formatter import IFormatter
from .json_formatter import JsonFormatter
from src.dtos.location import StorageObject


class FormatterFactory(IFormatterFactory):
    """Factory for creating formatter implementations."""

    def __init__(self):
        self._json_formatter = JsonFormatter()

    def get_formatter(self, object_type: StorageObject) -> IFormatter:
        """
        Get the appropriate formatter for the given object type.
        Currently all objects use JSON formatting.
        """
        if object_type == StorageObject.UNKNOWN:
            raise ValueError("Cannot get formatter for unknown object type")

        return self._json_formatter
