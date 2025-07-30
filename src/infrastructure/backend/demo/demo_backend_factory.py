from pathlib import Path

from src.dtos import DomainConfigDTO
from .demo_backend import DemoBackend
from .demo_naming_resolver import DemoNamingResolver
from .demo_query_handler import DemoQueryHandler

from src.infrastructure_ports import IBackendFactory

# Use project-root-relative paths for test fixtures
local_raw_data = Path("tests/fixtures/demo/raw")
local_db_data = Path("tests/fixtures/demo/dbs")


class DemoBackendFactory(IBackendFactory):
    def __init__(
        self, files_path: str = str(local_raw_data), db_path: str = str(local_db_data)
    ):
        self.files_path = files_path
        self.db_path = db_path

    def create(self, domain_config: DomainConfigDTO) -> DemoBackend:
        query_handler = DemoQueryHandler(domain_config=domain_config)
        naming_resolver = DemoNamingResolver(domain_cofig=domain_config)
        backend = DemoBackend(
            files_path=self.files_path,
            db_path=self.db_path,
            domain_config=domain_config,
            naming_resolver=naming_resolver,
            query_handler=query_handler,
        )
        return backend
