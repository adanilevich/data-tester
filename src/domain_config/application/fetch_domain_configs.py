from typing import List

from src.domain_config.ports import (
    FetchDomainConfigsCommand, IFetchDomainConfigsCommandHandler, INamingConventions,
    IStorage, ISerializer,
)
from src.domain_config import DomainConfigManager
from src.dtos import DomainConfigDTO


class FetchDomainConfigsCommandHandler(IFetchDomainConfigsCommandHandler):

    def __init__(
        self,
        naming_conventions: INamingConventions,
        storage: IStorage,
        serializer: ISerializer
    ):
        self.naming_conventions: INamingConventions = naming_conventions
        self.storage: IStorage = storage
        self.serializer: ISerializer = serializer

    def fetch(self, command: FetchDomainConfigsCommand) -> List[DomainConfigDTO]:

        manager = DomainConfigManager(
            naming_conventions=self.naming_conventions,
            storage=self.storage,
            serializer=self.serializer
        )

        domain_configs = manager.fetch_configs(location=command.location)

        return domain_configs
