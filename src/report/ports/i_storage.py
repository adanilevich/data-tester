from abc import ABC, abstractmethod
from typing import Any


class IStorage(ABC):

    @abstractmethod
    def save(self, content: Any, content_type: str, location: str):
        """
        Save report (content) to specified location. Storage handler should understand
        and resolve 'content_type' and based on the content type know how to persist
        the data on abtracted storage (e.g. as bytes or as text).
        """
