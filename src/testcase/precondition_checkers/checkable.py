from abc import ABC, abstractmethod
from typing import Dict


class AbstractCheckable(ABC):

    @abstractmethod
    def update_summary(self, summary: str):
        raise (NotImplementedError("Implement update_summary for your checkable"))

    @abstractmethod
    def add_detail(self, detail: Dict[str, str]):
        raise (NotImplementedError("Implement add_detail for your checkable"))

    @abstractmethod
    def notify(self, message: str):
        raise (NotImplementedError("Implement notify for your checkable"))
