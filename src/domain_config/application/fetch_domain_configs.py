from typing import List

from src.domain_config.ports import (
    FetchDomainConfigsCommand, IFetchDomainConfigsCommandHandler, INamingConventions,
    IStorage, IDomainConfigFormatter,
)
from src.domain_config import DomainConfig
from src.dtos import DomainConfigDTO


class FetchDomainConfigsCommandHandler(IFetchDomainConfigsCommandHandler):

    def __init__(
        self,
        naming_conventions: INamingConventions,
        storage: IStorage,
        serializer: IDomainConfigFormatter
    ):
        self.naming_conventions: INamingConventions = naming_conventions
        self.storage: IStorage = storage
        self.serializer: IDomainConfigFormatter = serializer

    def fetch(self, command: FetchDomainConfigsCommand) -> List[DomainConfigDTO]:

        manager = DomainConfig(
            naming_conventions=self.naming_conventions,
            storage=self.storage,
            formatter=self.serializer
        )

        domain_configs = manager.fetch_configs(location=command.location)

        return domain_configs
