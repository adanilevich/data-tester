from abc import ABC, abstractmethod
from typing import List


class IBackend(ABC):

    @abstractmethod
    def get_testobjects(self) -> List[str]:
        pass
