from abc import ABC, abstractmethod
from typing import Dict
from src.dtos import DomainConfigDTO

class FetchDomainConfigsCommand:
    def __init__(self, location: str):
        self.location = location
    def __eq__(self, other):
        return isinstance(other, FetchDomainConfigsCommand) and self.location == other.location

class IFetchDomainConfigsCommandHandler(ABC):
    @abstractmethod
    def fetch(self, command: FetchDomainConfigsCommand) -> Dict[str, DomainConfigDTO]:
        pass 