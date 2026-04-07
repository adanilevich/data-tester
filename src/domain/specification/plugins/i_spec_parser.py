from abc import ABC, abstractmethod

from src.dtos import SpecDTO, SpecType


class SpecParserError(Exception):
    """"""


class SpecDeserializationError(SpecParserError):
    """"""


class ISpecParser(ABC):
    """
    Interface for deserializing specification files from user-specific formats.
    """

    spec_type: SpecType

    @abstractmethod
    def parse(self, file: bytes, empty_spec: SpecDTO) -> SpecDTO:
        """
        Parses file and returns a valid SpecDTO object. In case of parsing errors,
        an EmptySpecDTO MUST be returned.
        """
        pass

    def set_message(self, spec: SpecDTO, message: str) -> SpecDTO:
        """
        Helper function to set messages on (empty) specs.
        """
        spec_ = spec.copy()
        spec_.message = message
        return spec_


class ISpecParserFactory(ABC):
    """
    Creates a formatter for a given specification type
    """

    @abstractmethod
    def get_parser(self, domain: str, spec_type: SpecType) -> ISpecParser:
        pass
