from src.testcase.ports import IDataPlatformFactory
from src.dtos.configs import DomainConfigDTO
from src.testcase.adapters.data_platforms.dummy import DummyPlatform


class DummyPlatformFactory(IDataPlatformFactory):

    def create(self, domain_config: DomainConfigDTO) -> DummyPlatform:
        return DummyPlatform()
