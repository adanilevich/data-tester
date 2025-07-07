from src.testcase.ports import IDataPlatformFactory
from src.dtos import DomainConfigDTO
from src.data_platform.dummy import DummyPlatform


class DummyPlatformFactory(IDataPlatformFactory):

    def create(self, domain_config: DomainConfigDTO) -> DummyPlatform:
        return DummyPlatform()
