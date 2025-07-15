from typing import Dict

from src.domain_config.ports import (
    IFetchDomainConfigsCommandHandler, FetchDomainConfigsCommand,
    ISaveDomainConfigCommandHandler, SaveDomainConfigCommand
)
from src.dtos import DomainConfigDTO, LocationDTO
from src.config import Config


class CLIDomainConfigManager:

    def __init__(
        self,
        fetch_command_handler: IFetchDomainConfigsCommandHandler,
        save_command_handler: ISaveDomainConfigCommandHandler,
        config: Config | None = None
    ):

        self.fetch_command_handler = fetch_command_handler
        self.save_command_handler = save_command_handler
        self.config = config or Config()

    def fetch_domain_configs(
        self, location: LocationDTO | None = None) -> Dict[str, DomainConfigDTO]:

        if location is None:
            if self.config.DATATESTER_DOMAIN_CONFIGS_LOCATION is None:
                raise ValueError("DOMAIN_CONFIGS_LOCATION undefined")
            else:
                location = LocationDTO(self.config.DATATESTER_DOMAIN_CONFIGS_LOCATION)
        else:
            location = location

        command = FetchDomainConfigsCommand(location=location)

        try:
            configs = self.fetch_command_handler.fetch(command=command)
        except Exception:
            configs = {}

        return configs

    def save_domain_config(self, location: LocationDTO, config: DomainConfigDTO):
        command = SaveDomainConfigCommand(location=location, config=config)
        self.save_command_handler.save(command=command)
