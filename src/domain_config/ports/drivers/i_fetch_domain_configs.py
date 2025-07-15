from abc import ABC, abstractmethod
from typing import Dict
from src.dtos import DomainConfigDTO, DTO, LocationDTO


class FetchDomainConfigsCommand(DTO):
    location: LocationDTO


class IFetchDomainConfigsCommandHandler(ABC):
    @abstractmethod
    def fetch(self, command: FetchDomainConfigsCommand) -> Dict[str, DomainConfigDTO]:
        pass
