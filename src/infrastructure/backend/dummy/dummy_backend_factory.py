from src.infrastructure.backend.i_backend_factory import IBackendFactory
from src.dtos import DomainConfigDTO
from src.infrastructure.backend.dummy.dummy_backend import DummyBackend


class DummyBackendFactory(IBackendFactory):
    def create(self, domain_config: DomainConfigDTO) -> DummyBackend:
        return DummyBackend()
