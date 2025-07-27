from typing import Dict, cast

from src.storage.i_storage import IStorage, StorageError
from src.dtos import DomainConfigDTO, LocationDTO, StorageObject


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
    def __init__(self, storage: IStorage):
        self.storage: IStorage = storage

    def fetch_configs(self, location: LocationDTO) -> Dict[str, DomainConfigDTO]:
        """
        Parses all files in the given location that match the domain config naming
        conventions, deserializes their contents, and converts them into DomainConfigDTO
        objects. Since we are potentially reading from user-managed locations, unparseable
        files and files which don't correspond to the domain config naming conventions
        are ignored.

        Args:
            location (str): The path or location where domain config files are stored.

        Returns:
            Dict[str, DomainConfigDTO]: A dictionary domain names
            to their corresponding DomainConfigDTO objects. Files that cannot be
            parsed or do not match the conventions are ignored.

        Raises:
            ValueError: If the provided location is not a string.
            DomainConfigAlreadyExistsError: If a domain config for the same domain
            already exists.
        """

        found_domain_configs: Dict[str, DomainConfigDTO] = {}

        try:
            config_locations = self.storage.list(
                location=location, object_type=StorageObject.DOMAIN_CONFIG
            )
        except StorageError as err:
            raise StorageError(f"Failed to list domain configs in {location}") from err

        for config_location in config_locations:
            try:
                config_dto = self.storage.read(
                    object_type=StorageObject.DOMAIN_CONFIG,
                    object_id=config_location.located_object_id,
                    location=location,
                )
                config = cast(DomainConfigDTO, config_dto)
            except (
                StorageError,
                DomainConfigSerializationError,
                DomainConfigParsingError,
            ):
                continue

            if config.domain in found_domain_configs:
                msg = f"Domain config for {config.domain} already exists"
                raise DomainConfigAlreadyExistsError(msg)
            else:
                found_domain_configs[config.domain] = config

        return found_domain_configs

    def save_config(self, location: LocationDTO, config: DomainConfigDTO):
        """
        Saves a domain config to the given location.

        Args:
            location (str): The path or location where the domain config will be saved.
            config (DomainConfigDTO): The domain config to save.

        Raises:
            DomainConfigAlreadyExistsError: If a domain config for the same domain
        """

        self.storage.write(config, StorageObject.DOMAIN_CONFIG, location)
