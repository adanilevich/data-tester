from abc import ABC, abstractmethod

class DomainConfigFormatterError(Exception):
    """"""

class IDomainConfigFormatter(ABC):
    @abstractmethod
    def deserialize(self, content: bytes) -> dict:
        """
        Parses / deserializes domain config from bytecontent to dictionary.
        Raises:
            DomainConfigFormatterError
        """

    @abstractmethod
    def serialize(self, content: dict) -> bytes:
        """
        Serializes a domain config (or any dictionary) to bytes.
        Raises:
            DomainConfigFormatterError
        """
