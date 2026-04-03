from typing import Dict

from src.domain_ports import (
    IDomainConfig,
    ListDomainConfigsCommand,
    LoadDomainConfigCommand,
    SaveDomainConfigCommand,
)
from src.dtos import DomainConfigDTO


class DomainConfigDriver:
    def __init__(self, domain_config_handler: IDomainConfig):
        self.domain_config_handler = domain_config_handler

    def list_domain_configs(self) -> Dict[str, DomainConfigDTO]:
        """Fetches all domain configs."""
        command = ListDomainConfigsCommand()
        return self.domain_config_handler.list_domain_configs(command=command)

    def save_domain_config(self, config: DomainConfigDTO) -> None:
        """Saves a domain config."""
        command = SaveDomainConfigCommand(config=config)
        self.domain_config_handler.save_domain_config(command=command)

    def load_domain_config(self, domain: str) -> DomainConfigDTO:
        """Loads a single domain config by domain name."""
        command = LoadDomainConfigCommand(domain=domain)
        return self.domain_config_handler.load_domain_config(command=command)
