from abc import ABC, abstractmethod
from typing import List

from src.dtos import DTO, DBInstanceDTO, DomainConfigDTO, TestObjectDTO


class ListTestObjectsCommand(DTO):
    domain_config: DomainConfigDTO
    db: DBInstanceDTO


class IPlatform(ABC):
    @abstractmethod
    def list_testobjects(self, command: ListTestObjectsCommand) -> List[TestObjectDTO]:
        """List available testobjects in the platform."""
