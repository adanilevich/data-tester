from typing import Dict
from src.domain_ports import (
    IDomainConfigHandler,
    FetchDomainConfigsCommand,
    SaveDomainConfigCommand,
)
from src.infrastructure_ports import IStorageFactory
from .domain_config import DomainConfig
from src.dtos import DomainConfigDTO


class DomainConfigHandler(IDomainConfigHandler):
    """
    Implementation of IDomainConfigHandler for fetching and saving domain configs.
    """

    def __init__(self, storage_factory: IStorageFactory):
        """
        Initialize the handler with a storage factory.
        Args:
            storage_factory (IStorageFactory): The storage factory to use for
                domain configs.
        """
        self.storage_factory = storage_factory

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
        storage = self.storage_factory.get_storage(command.location)
        manager = DomainConfig(storage=storage)
        domain_configs = manager.fetch_configs(location=command.location)
        return domain_configs

    def save_domain_config(self, command: SaveDomainConfigCommand) -> None:
        """
        Save a domain config to the specified location using the storage backend.
        Args:
            command (SaveDomainConfigCommand): The command containing the config and
                location to save to.
        """
        storage = self.storage_factory.get_storage(command.location)
        manager = DomainConfig(storage=storage)
        manager.save_config(location=command.location, config=command.config)
