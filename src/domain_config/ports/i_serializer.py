from abc import ABC, abstractmethod


class SerializerError(Exception):
    """"""


class ISerializer(ABC):

    open_mode: str  # "r" or "b" - mode how domain config is read/writted to storage

    @abstractmethod
    def from_string(self, content: str) -> dict:
        """
        Parses string-valued object ad returns a dict which is then used for domain conf.
        Must raise ParsingError in case of any parsing errors.
        """

    @abstractmethod
    def from_bytes(self, content: bytes) -> dict:
        """
        Parses bytes-valued object and returns a dict which is then used for domain conf.
        Must raise ParsingError in case of any parsing errors.
        """

    @abstractmethod
    def to_string(self, content: dict) -> str:
        """
        Serializes a domain config (or any dictionary) to a string-based format
        """

    @abstractmethod
    def to_bytes(self, content: dict) -> bytes:
        """
        Serializes a domain config (or any dictionary) to a bytes-based format
        """
