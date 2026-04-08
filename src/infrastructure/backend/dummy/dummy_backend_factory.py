from src.dtos import DomainConfigDTO
from src.infrastructure.backend.dummy.dummy_backend import DummyBackend
from src.infrastructure_ports import IBackendFactory


class DummyBackendFactory(IBackendFactory):
    def create(self, domain_config: DomainConfigDTO) -> DummyBackend:
        return DummyBackend()
