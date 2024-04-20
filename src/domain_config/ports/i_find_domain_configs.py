from abc import abstractmethod, ABC
from typing import List

from src.dtos import DTO, DomainConfigDTO


class FindDomainConfigsCommand(DTO):
    locations: List[str]


class IFindDomainConfigsCommandHandler(ABC):

    @abstractmethod
    def find(self, command: FindDomainConfigsCommand) -> List[DomainConfigDTO]:
        """
        Given a list of locations (to folders or files), searches and fetches
        domain configs from these locations
        """
