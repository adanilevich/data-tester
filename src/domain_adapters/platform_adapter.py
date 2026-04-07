from typing import List

from src.domain_ports import IPlatform, ListTestObjectsCommand
from src.dtos import TestObjectDTO
from src.infrastructure_ports import IBackendFactory


class PlatformAdapter(IPlatform):
    def __init__(self, backend_factory: IBackendFactory):
        self.backend_factory = backend_factory

    def list_testobjects(self, command: ListTestObjectsCommand) -> List[TestObjectDTO]:
        backend = self.backend_factory.create(command.domain_config)
        return backend.list_testobjects(command.db)
