from typing import List

from src.domain_ports import IPlatform, ListTestObjectsCommand
from src.dtos import DBInstanceDTO, DomainConfigDTO, TestObjectDTO


class PlatformDriver:
    def __init__(self, platform_adapter: IPlatform):
        self.adapter = platform_adapter

    def list_testobjects(
        self, domain_config: DomainConfigDTO, db: DBInstanceDTO
    ) -> List[TestObjectDTO]:
        command = ListTestObjectsCommand(domain_config=domain_config, db=db)
        return self.adapter.list_testobjects(command)
