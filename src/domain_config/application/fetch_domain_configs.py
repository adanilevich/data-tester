from typing import Dict

from src.domain_config.ports import (
    FetchDomainConfigsCommand, IFetchDomainConfigsCommandHandler,IStorage,
)
from src.domain_config.core import DomainConfig
from src.dtos import DomainConfigDTO


class FetchDomainConfigsCommandHandler(IFetchDomainConfigsCommandHandler):

    def __init__(self, storage: IStorage):
        self.storage: IStorage = storage

    def fetch(self, command: FetchDomainConfigsCommand) -> Dict[str, DomainConfigDTO]:

        manager = DomainConfig(storage=self.storage)
        domain_configs = manager.fetch_configs(location=command.location)

        return domain_configs
