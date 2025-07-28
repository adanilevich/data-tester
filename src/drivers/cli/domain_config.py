from typing import Dict

from src.domain.domain_config import IDomainConfigHandler, FetchDomainConfigsCommand
from src.dtos import DomainConfigDTO, LocationDTO


class CLIDomainConfigManager:
    def __init__(
        self,
        domain_config_handler: IDomainConfigHandler,
        domain_config_location: LocationDTO,
    ):
        self.domain_config_handler = domain_config_handler
        self.domain_config_location = domain_config_location

    def fetch_domain_configs(self) -> Dict[str, DomainConfigDTO]:
        """Fetches domain configs from the configured location"""

        command = FetchDomainConfigsCommand(location=self.domain_config_location)
        configs = self.domain_config_handler.fetch_domain_configs(command=command)

        return configs
