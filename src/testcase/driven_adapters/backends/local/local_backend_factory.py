from src.dtos.configs import DomainConfigDTO
from src.testcase.driven_adapters.backends.local import (
    LocalBackend, DemoNamingResolver, DemoQueryHandler
)
from src.testcase.driven_ports.i_backend_factory import IBackendFactory
from pathlib import Path

PATH = Path(__file__).parent
local_raw_data = PATH.parent.parent.parent.parent.parent / "tests/data/data/raw"
local_db_data = PATH.parent.parent.parent.parent.parent / "tests/data/data/dbs"


class LocalBackendFactory(IBackendFactory):

    def __init__(self, files_path: str = str(local_raw_data),
                 db_path: str = str(local_db_data)):
        self.files_path = files_path
        self.db_path = db_path

    def create(self, domain_config: DomainConfigDTO) -> LocalBackend:
        query_handler = DemoQueryHandler(domain_config=domain_config)
        naming_resolver = DemoNamingResolver(domain_cofig=domain_config)
        backend = LocalBackend(
            files_path=self.files_path,
            db_path=self.db_path,
            domain_config=domain_config,
            naming_resolver=naming_resolver,
            query_handler=query_handler
        )
        return backend
