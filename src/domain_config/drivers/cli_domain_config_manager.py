from typing import Dict

from src.domain_config.ports import (
    IDomainConfigHandler, FetchDomainConfigsCommand, SaveDomainConfigCommand
)
from src.dtos import DomainConfigDTO, LocationDTO
from src.config import Config


class CLIDomainConfigManager:
    def __init__(
        self,
        domain_config_handler: IDomainConfigHandler,
        config: Config | None = None
    ):
        self.domain_config_handler = domain_config_handler
        self.config = config or Config()

    def fetch_domain_configs(
        self, location: LocationDTO | None = None
    ) -> Dict[str, DomainConfigDTO]:
        if location is None:
            if self.config.DATATESTER_DOMAIN_CONFIGS_LOCATION is None:
                raise ValueError("DOMAIN_CONFIGS_LOCATION undefined")
            else:
                location = LocationDTO(
                    self.config.DATATESTER_DOMAIN_CONFIGS_LOCATION
                )
        else:
            location = location

        command = FetchDomainConfigsCommand(location=location)

        try:
            configs = self.domain_config_handler.fetch_domain_configs(command=command)
        except Exception:
            configs = {}

        return configs

    def save_domain_config(
        self, location: LocationDTO, config: DomainConfigDTO
    ):
        command = SaveDomainConfigCommand(location=location, config=config)
        self.domain_config_handler.save_domain_config(command=command)
