from src.testcase.ports.i_backend_factory import IBackendFactory
from src.dtos.configs import DomainConfigDTO
from src.testcase.adapters.backends.dummy.dummy_backend import DummyBackend


class DummyBackendFactory(IBackendFactory):

    def create(self, domain_config: DomainConfigDTO) -> DummyBackend:
        return DummyBackend()
