from abc import ABC, abstractmethod
from typing import List, Optional


class IStorage(ABC):
    """Dont know yet"""

    @abstractmethod
    def list_objects(self, location: str) -> List[str]:
        """"Lists all potential domain config objects, e.g. files"""

    @abstractmethod
    def is_valid_location(self, location: str) -> bool:
        """"Checks if given location is valid"""

    @abstractmethod
    def load_object(self, location: str) -> Optional[bytes | str]:
        """Loads object defined in location and returnes as bytes"""
