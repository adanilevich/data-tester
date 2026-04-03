from typing import Dict

from src.domain_ports import (
    IDomainConfig,
    ListDomainConfigsCommand,
    LoadDomainConfigCommand,
    SaveDomainConfigCommand,
)
from src.dtos import DomainConfigDTO


class DomainConfigDriver:
    def __init__(self, domain_config_adapter: IDomainConfig):
        self.adapter = domain_config_adapter

    def list_domain_configs(self) -> Dict[str, DomainConfigDTO]:
        """Fetches all domain configs."""
        command = ListDomainConfigsCommand()
        return self.adapter.list_domain_configs(command=command)

    def save_domain_config(self, config: DomainConfigDTO) -> None:
        """Saves a domain config."""
        command = SaveDomainConfigCommand(config=config)
        self.adapter.save_domain_config(command=command)

    def load_domain_config(self, domain: str) -> DomainConfigDTO:
        """Loads a single domain config by domain name."""
        command = LoadDomainConfigCommand(domain=domain)
        return self.adapter.load_domain_config(command=command)
