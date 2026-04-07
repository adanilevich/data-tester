from typing import Dict, cast

from src.dtos import DomainConfigDTO, ObjectType
from src.infrastructure_ports import IDtoStorage, StorageError


class DomainConfigNotUniqueError(Exception):
    """
    Exception raised when a domain config for the same domain already exists.
    """


class DomainConfig:
    def __init__(self, storage: IDtoStorage):
        self.storage: IDtoStorage = storage

    def load(self, domain: str) -> DomainConfigDTO:
        """Loads a single domain config by domain name."""
        dto = self.storage.read_dto(object_type=ObjectType.DOMAIN_CONFIG, id=domain)
        return cast(DomainConfigDTO, dto)

    def save(self, config: DomainConfigDTO) -> None:
        """
        Saves a domain config to internal storage.

        Args:
            config (DomainConfigDTO): The domain config to save.
        """
        self.storage.write_dto(config)

    def list(self) -> Dict[str, DomainConfigDTO]:
        """
        Lists all domain configs from internal storage and returns them
        as a dictionary keyed by domain name. Unparseable configs are
        silently skipped.

        Returns:
            Dict[str, DomainConfigDTO]: A dictionary mapping domain names
            to their corresponding DomainConfigDTO objects.

        Raises:
            DomainConfigAlreadyExistsError: If a domain config for the
            same domain already exists.
        """

        found_domain_configs: Dict[str, DomainConfigDTO] = {}

        try:
            config_dtos = self.storage.list_dtos(object_type=ObjectType.DOMAIN_CONFIG)
        except StorageError as err:
            raise StorageError("Failed to list domain configs") from err

        for dto in config_dtos:
            config = cast(DomainConfigDTO, dto)
            if config.domain in found_domain_configs:
                raise DomainConfigNotUniqueError(config.domain)
            else:
                found_domain_configs[config.domain] = config

        return found_domain_configs
