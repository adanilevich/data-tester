from abc import ABC, abstractmethod
from typing import Any


class IStorage(ABC):

    @abstractmethod
    def save(self, content: Any, format: str, location: str):
        """Save content to specified location"""
