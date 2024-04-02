from abc import ABC, abstractmethod
from typing import List


class IBackend(ABC):

    @abstractmethod
    def get_testobjects(self, domain: str, project: str, instance) -> List[str]:
        pass