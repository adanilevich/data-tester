from typing import Dict
from src.domain_config.ports.drivers.i_domain_config_handler import (
    IDomainConfigHandler,
    FetchDomainConfigsCommand,
    SaveDomainConfigCommand,
)
from src.storage.i_storage import IStorage
from src.domain_config.core import DomainConfig
from src.dtos import DomainConfigDTO


class DomainConfigHandler(IDomainConfigHandler):
    """
    Implementation of IDomainConfigHandler for fetching and saving domain configs.
    """

    def __init__(self, storage: IStorage):
        """
        Initialize the handler with a storage backend.
        Args:
            storage (IStorage): The storage backend to use for domain configs.
        """
        self.storage = storage

    def fetch_domain_configs(
        self, command: FetchDomainConfigsCommand
    ) -> Dict[str, DomainConfigDTO]:
        """
        Fetch all domain configs from the specified location using the storage backend.
        Args:
            command (FetchDomainConfigsCommand): The command containing the location to
                fetch from.
        Returns:
            Dict[str, DomainConfigDTO]: A dictionary mapping domain names to
            corresponding domain configs.
        """
        manager = DomainConfig(storage=self.storage)
        domain_configs = manager.fetch_configs(location=command.location)
        return domain_configs

    def save_domain_config(self, command: SaveDomainConfigCommand) -> None:
        """
        Save a domain config to the specified location using the storage backend.
        Args:
            command (SaveDomainConfigCommand): The command containing the config and
                location to save to.
        """
        manager = DomainConfig(storage=self.storage)
        manager.save_config(location=command.location, config=command.config)
