from abc import abstractmethod, ABC
from typing import List

from src.dtos import DTO, DomainConfigDTO


class FetchDomainConfigsCommand(DTO):
    location: str


class IFetchDomainConfigsCommandHandler(ABC):

    @abstractmethod
    def fetch(self, command: FetchDomainConfigsCommand) -> List[DomainConfigDTO]:
        """
        Given a list of locations (to folders or files), searches and fetches
        domain configs from these locations
        """
