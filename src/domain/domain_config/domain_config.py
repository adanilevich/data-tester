from typing import Dict, cast

from src.infrastructure_ports import IDtoStorage, StorageError
from src.dtos import DomainConfigDTO, ObjectType


class DomainConfigAlreadyExistsError(Exception):
    """
    Exception raised when a domain config for the same domain already exists.
    """


class DomainConfigSerializationError(Exception):
    """
    Exception raised when a domain config cannot be serialized or deserialized.
    """


class DomainConfigParsingError(Exception):
    """
    Exception raised when a domain config cannot be parsed.
    """


class DomainConfig:
    # TODO: implement read_config method
    def __init__(self, storage: IDtoStorage):
        self.storage: IDtoStorage = storage

    # TODO: rename to list_configs
    def fetch_configs(self) -> Dict[str, DomainConfigDTO]:
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
            config_dtos = self.storage.list_dtos(
                object_type=ObjectType.DOMAIN_CONFIG
            )
        except StorageError as err:
            raise StorageError(
                "Failed to list domain configs"
            ) from err

        for dto in config_dtos:
            config = cast(DomainConfigDTO, dto)
            if config.domain in found_domain_configs:
                msg = (
                    f"Domain config for {config.domain} already exists"
                )
                raise DomainConfigAlreadyExistsError(msg)
            else:
                found_domain_configs[config.domain] = config

        return found_domain_configs

    def save_config(self, config: DomainConfigDTO) -> None:
        """
        Saves a domain config to internal storage.

        Args:
            config (DomainConfigDTO): The domain config to save.
        """
        self.storage.write_dto(config)
