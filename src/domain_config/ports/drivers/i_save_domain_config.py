from abc import ABC, abstractmethod
from src.dtos import DomainConfigDTO

class SaveDomainConfigCommand:
    def __init__(self, config: DomainConfigDTO, location: str):
        self.config = config
        self.location = location

class ISaveDomainConfigCommandHandler(ABC):
    @abstractmethod
    def save(self, command: SaveDomainConfigCommand) -> None:
        pass 