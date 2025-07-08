from typing import Dict

from src.domain_config.ports import (
    IFetchDomainConfigsCommandHandler, FetchDomainConfigsCommand,
    ISaveDomainConfigCommandHandler, SaveDomainConfigCommand
)
from src.dtos import DomainConfigDTO
from src.config import Config


class DomainConfigManager:

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
        self, location: str | None = None) -> Dict[str, DomainConfigDTO]:

        location = location or self.config.DATATESTER_DOMAIN_CONFIGS_LOCATION
        if location is None:
            raise ValueError("DOMAIN_CONFIGS_LOCATION undefined")

        command = FetchDomainConfigsCommand(location=location)

        try:
            configs = self.fetch_command_handler.fetch(command=command)
        except Exception:
            configs = {}

        return configs

    def save_domain_config(self, location: str, config: DomainConfigDTO):
        command = SaveDomainConfigCommand(location=location, config=config)
        self.save_command_handler.save(command=command)
