from pathlib import Path

from src.dtos import DomainConfigDTO
from src.infrastructure_ports import IBackendFactory

from .demo_backend import DemoBackend
from .demo_naming_resolver import DemoNamingResolver
from .demo_query_handler import DemoQueryHandler

# Use project-root-relative paths for test fixtures
local_raw_data = Path("tests/fixtures/demo/data/raw")
local_db_data = Path("tests/fixtures/demo/data/dbs")


class DemoBackendFactory(IBackendFactory):
    """Builds a fresh DemoBackend (with its own DuckDB connection) per call.

    The factory used to cache one backend per domain, but that meant every
    worker thread in a TestRun shared the same backend — and therefore the
    same DuckDB session — which deadlocked under concurrent DDL/DML. With no
    caching each testcase gets its own backend and its own connection, so
    there is nothing to contend on.
    """

    def __init__(
        self,
        files_path: str = str(local_raw_data),
        db_path: str = str(local_db_data),
    ):
        self.files_path = files_path
        self.db_path = db_path

    def create(self, domain_config: DomainConfigDTO) -> DemoBackend:
        query_handler = DemoQueryHandler(domain_config=domain_config)
        naming_resolver = DemoNamingResolver(domain_cofig=domain_config)
        return DemoBackend(
            files_path=self.files_path,
            db_path=self.db_path,
            domain_config=domain_config,
            naming_resolver=naming_resolver,
            query_handler=query_handler,
        )
