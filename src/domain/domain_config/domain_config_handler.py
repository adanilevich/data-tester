from typing import Dict
from src.domain_ports import (
    IDomainConfigHandler,
    FetchDomainConfigsCommand,
    SaveDomainConfigCommand,
)
from src.infrastructure_ports import IDtoStorage
from .domain_config import DomainConfig
from src.dtos import DomainConfigDTO

# TODO: rename module to handle_domain_configs.py

class DomainConfigHandler(IDomainConfigHandler):
    # TODO: implement load_domain_config and save_domain_config methods
    """
    Implementation of IDomainConfigHandler for fetching and saving domain configs.
    """

    def __init__(self, dto_storage: IDtoStorage):
        self.dto_storage = dto_storage

    # TODO: rename to list_domain_configs
    def fetch_domain_configs(
        self, command: FetchDomainConfigsCommand
    ) -> Dict[str, DomainConfigDTO]:
        manager = DomainConfig(storage=self.dto_storage)
        return manager.fetch_configs()

    # TODO
    def save_domain_config(self, command: SaveDomainConfigCommand) -> None:
        manager = DomainConfig(storage=self.dto_storage)
        manager.save_config(config=command.config)
