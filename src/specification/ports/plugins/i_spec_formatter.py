from abc import ABC, abstractmethod

from src.dtos import (
    SpecificationType, SpecificationFormat, SpecContent
)


class ISpecFormatter(ABC):
    """
    Interface for deserializing specification files from user-specific formats.
    """
    spec_type: SpecificationType
    spec_format: SpecificationFormat

    @abstractmethod
    def deserialize(self, file: bytes) -> SpecContent:
        pass


class ISpecFormatterFactory(ABC):
    """
    Creates a formatter for a given specification type
    """
    @abstractmethod
    def get_formatter(self, spec_type: SpecificationType) -> ISpecFormatter:
        pass
