from abc import ABC, abstractmethod

from src.dtos import DomainConfigDTO
from src.infrastructure_ports.i_backend import IBackend


class IBackendFactory(ABC):
    @abstractmethod
    def create(self, domain_config: DomainConfigDTO) -> IBackend:
        """Will dynamically create and parametrize data_platforms based on config"""
