from src.infrastructure_ports import IBackendFactory
from src.dtos import DomainConfigDTO
from src.infrastructure.backend.dummy.dummy_backend import DummyBackend


class DummyBackendFactory(IBackendFactory):
    def create(self, domain_config: DomainConfigDTO) -> DummyBackend:
        return DummyBackend()
