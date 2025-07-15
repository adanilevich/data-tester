from abc import ABC, abstractmethod
from typing import Dict
from src.dtos import DomainConfigDTO, DTO, LocationDTO


class FetchDomainConfigsCommand(DTO):
    """
    Command object for fetching domain configs from a given location.
    """

    location: LocationDTO


class SaveDomainConfigCommand(DTO):
    """
    Command object for saving a domain config to a given location.
    """

    config: DomainConfigDTO
    location: LocationDTO


class IDomainConfigHandler(ABC):
    """
    Interface for handling domain config operations such as fetch and save.
    """

    @abstractmethod
    def fetch_domain_configs(
        self, command: FetchDomainConfigsCommand
    ) -> Dict[str, DomainConfigDTO]:
        """
        Fetch all domain configs from the specified location.
        Args:
            command (FetchDomainConfigsCommand): The command containing the location to
                fetch from.
        Returns:
            Dict[str, DomainConfigDTO]: A dictionary mapping domain names to
            corresponding domain configs.
        """
        pass

    @abstractmethod
    def save_domain_config(self, command: SaveDomainConfigCommand) -> None:
        """
        Save a domain config to the specified location.
        Args:
            command (SaveDomainConfigCommand): The command containing the config and
                location to save to.
        """
        pass
