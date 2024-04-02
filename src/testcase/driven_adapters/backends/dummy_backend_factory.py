from src.testcase.driven_ports.backend_factory_interface import IBackendFactory
from src.testcase.dtos import DomainConfigDTO
from src.testcase.driven_adapters.backends.dummy_backend import DummyBackend


class DummyBackendFactory(IBackendFactory):

    def create(self, domain_config: DomainConfigDTO) -> DummyBackend:
        return DummyBackend()
