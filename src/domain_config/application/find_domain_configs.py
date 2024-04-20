from typing import List

from src.domain_config.ports import (
    FindDomainConfigsCommand, IFindDomainConfigsCommandHandler, INamingConventions,
    IStorage, IParser,
)
from src.domain_config import DomainConfigManager
from src.dtos import DomainConfigDTO


class FindDomainConfigsCommandHandler(IFindDomainConfigsCommandHandler):

    def __init__(
        self,
        naming_conventions: INamingConventions,
        storage: IStorage,
        parser: IParser
    ):
        self. naming_conventions: INamingConventions = naming_conventions
        self.storage: IStorage = storage
        self.parser: IParser = parser

    def find(self, command: FindDomainConfigsCommand) -> List[DomainConfigDTO]:
        domain_config_finder = DomainConfigManager(
            naming_conventions=self.naming_conventions,
            storage=self.storage,
            parser=self.parser
        )

        domain_configs = domain_config_finder.find(locations=command.locations)

        return domain_configs
