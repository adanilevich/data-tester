from abc import ABC, abstractmethod


class IParser(ABC):

    @abstractmethod
    def parse(self, content: bytes | str) -> dict:
        """Parses provided object ad returns a dict which is then used for domain conf."""
