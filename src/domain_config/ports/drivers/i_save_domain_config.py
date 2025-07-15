from abc import ABC, abstractmethod
from src.dtos import DomainConfigDTO, DTO, LocationDTO


class SaveDomainConfigCommand(DTO):
    config: DomainConfigDTO
    location: LocationDTO


class ISaveDomainConfigCommandHandler(ABC):
    @abstractmethod
    def save(self, command: SaveDomainConfigCommand) -> None:
        pass
