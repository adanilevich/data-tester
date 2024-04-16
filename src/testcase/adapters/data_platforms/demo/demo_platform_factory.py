from src.dtos.configs import DomainConfigDTO
from src.testcase.adapters.data_platforms.demo import (
    LocalDataPlatform, DemoNamingResolver, DemoQueryHandler
)
from src.testcase.ports import IDataPlatformFactory
from pathlib import Path

PATH = Path(__file__).parent
local_raw_data = PATH.parent.parent.parent.parent.parent / "tests/data/data/raw"
local_db_data = PATH.parent.parent.parent.parent.parent / "tests/data/data/dbs"


class LocalDataPlatformFactory(IDataPlatformFactory):

    def __init__(self, files_path: str = str(local_raw_data),
                 db_path: str = str(local_db_data)):
        self.files_path = files_path
        self.db_path = db_path

    def create(self, domain_config: DomainConfigDTO) -> LocalDataPlatform:
        query_handler = DemoQueryHandler(domain_config=domain_config)
        naming_resolver = DemoNamingResolver(domain_cofig=domain_config)
        backend = LocalDataPlatform(
            files_path=self.files_path,
            db_path=self.db_path,
            domain_config=domain_config,
            naming_resolver=naming_resolver,
            query_handler=query_handler
        )
        return backend
