from abc import ABC, abstractmethod
from src.testcase.ports.i_data_platform import IDataPlatform
from src.dtos import DomainConfigDTO


class IDataPlatformFactory(ABC):

    @abstractmethod
    def create(self, domain_config: DomainConfigDTO) -> IDataPlatform:
        """Will dynamically create and parametrize data_platforms based on config"""
