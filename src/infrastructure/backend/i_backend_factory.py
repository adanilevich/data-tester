from abc import ABC, abstractmethod
from src.infrastructure.backend.i_backend import IBackend
from src.dtos import DomainConfigDTO


class IBackendFactory(ABC):
    @abstractmethod
    def create(self, domain_config: DomainConfigDTO) -> IBackend:
        """Will dynamically create and parametrize data_platforms based on config"""
