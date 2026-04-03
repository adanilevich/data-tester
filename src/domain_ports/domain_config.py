from abc import ABC, abstractmethod
from typing import Dict
from src.dtos import DomainConfigDTO, DTO


#TODO: implement LoadDomainConfigCommand and SaveDomainConfigCommand and methods

#TODO: rename to ListDomainConfigsCommand
class FetchDomainConfigsCommand(DTO):
    """
    Command object for fetching domain configs.
    """


class SaveDomainConfigCommand(DTO):
    """
    Command object for saving a domain config.
    """

    config: DomainConfigDTO


class IDomainConfigHandler(ABC):
    """
    Interface for handling domain config operations such as fetch and save.
    """
    #TODO: rename to list_domain_configs
    @abstractmethod
    def fetch_domain_configs(
        self, command: FetchDomainConfigsCommand
    ) -> Dict[str, DomainConfigDTO]:
        """
        Fetch all domain configs.
        """
        pass

    @abstractmethod
    def save_domain_config(
        self, command: SaveDomainConfigCommand
    ) -> None:
        """
        Save a domain config.
        """
        pass
