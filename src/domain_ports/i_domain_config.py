from abc import ABC, abstractmethod
from typing import Dict
from src.dtos import DomainConfigDTO, DTO


class ListDomainConfigsCommand(DTO):
    """Command object for fetching domain configs."""


class SaveDomainConfigCommand(DTO):
    """Command object for saving a domain config."""

    config: DomainConfigDTO


class LoadDomainConfigCommand(DTO):
    """Command object for loading a single domain config by domain name."""

    domain: str


class IDomainConfig(ABC):
    """Interface for handling domain config operations."""

    @abstractmethod
    def list_domain_configs(
        self, command: ListDomainConfigsCommand
    ) -> Dict[str, DomainConfigDTO]:
        """Fetch all domain configs from internal storage."""

    @abstractmethod
    def save_domain_config(self, command: SaveDomainConfigCommand) -> None:
        """Save a domain config to internal storage."""

    @abstractmethod
    def load_domain_config(self, command: LoadDomainConfigCommand) -> DomainConfigDTO:
        """Load a single domain config by domain name."""
