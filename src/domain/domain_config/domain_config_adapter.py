from typing import Dict
from src.domain_ports import (
    IDomainConfig,
    ListDomainConfigsCommand,
    LoadDomainConfigCommand,
    SaveDomainConfigCommand,
)
from src.infrastructure_ports import IDtoStorage
from .domain_config import DomainConfig
from src.dtos import DomainConfigDTO


class DomainConfigAdapter(IDomainConfig):
    """Implementation of IDomainConfigHandler for domain config operations."""

    def __init__(self, dto_storage: IDtoStorage):
        self.dto_storage = dto_storage

    def list_domain_configs(
        self, command: ListDomainConfigsCommand
    ) -> Dict[str, DomainConfigDTO]:
        manager = DomainConfig(storage=self.dto_storage)
        return manager.list()

    def save_domain_config(self, command: SaveDomainConfigCommand) -> None:
        manager = DomainConfig(storage=self.dto_storage)
        manager.save(config=command.config)

    def load_domain_config(self, command: LoadDomainConfigCommand) -> DomainConfigDTO:
        manager = DomainConfig(storage=self.dto_storage)
        return manager.load(domain=command.domain)
