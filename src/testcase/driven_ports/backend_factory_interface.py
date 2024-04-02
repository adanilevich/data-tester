from abc import ABC, abstractmethod
from src.testcase.driven_ports.backend_interface import IBackend
from src.testcase.dtos import DomainConfigDTO


class IBackendFactory(ABC):

    @abstractmethod
    def create(self, domain_config: DomainConfigDTO) -> IBackend:
        """Will dynamically create and parametrize backends based on config"""
