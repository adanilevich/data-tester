from typing import List, Dict
import yaml  # type: ignore
import re

from src.storage.i_storage import IStorage, StorageError
from src.dtos import DomainConfigDTO
from src.dtos.location import LocationDTO


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

    def _match_filename(self, filename: str) -> bool:
        """
        Checks if a filename matches the domain config naming conventions.
        """
        # Match files containing 'domain_config' not preceded by an underscore,
        # before .yaml/.yml
        match = re.match(
            r"^(?!_).*domain_config.*\.(yaml|yml)$", filename, re.IGNORECASE
        )
        return bool(match)

    def _get_filename(self, config: DomainConfigDTO) -> str:
        """
        Returns the conventionally-correct filename for a given domain config.
        """
        return "domain_config_" + config.domain + ".yaml"

    def _find_candidates(self, location: LocationDTO) -> List[LocationDTO]:
        """Gets valid, name-matching objects from location"""

        try:
            objects = self.storage.list(path=location)
        except StorageError:
            objects = []

        candidates = [obj for obj in objects if self._match_filename(obj.path)]
        return candidates

    def _config_from_yaml_bytes(self, content: bytes) -> DomainConfigDTO:
        """
        Deserializes a domain config from a YAML bytes object.
        """

        try:
            config_as_dict = yaml.safe_load(content)
        except Exception as e:
            msg = f"Failed to deserialize YAML: {e}"
            raise DomainConfigSerializationError(msg) from e
        try:
            return DomainConfigDTO.from_dict(config_as_dict)
        except Exception as e:
            msg = f"Failed to parse YAML: {e}"
            raise DomainConfigParsingError(msg) from e

    def _config_to_yaml_bytes(self, config: DomainConfigDTO) -> bytes:
        """
        Serializes a domain config to a YAML bytes object.
        """
        try:
            return yaml.safe_dump(config.to_dict(), allow_unicode=True).encode()
        except Exception as e:
            msg = f"Failed to serialize YAML: {e}"
            raise DomainConfigSerializationError(msg) from e

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

        candidates: List[LocationDTO] = []
        found_domain_configs: Dict[str, DomainConfigDTO] = {}

        candidates = self._find_candidates(location)

        for candidate in candidates:
            config: DomainConfigDTO | None = None

            try:
                config_as_bytes = self.storage.read(path=candidate)
                config = self._config_from_yaml_bytes(config_as_bytes)
            except (
                StorageError, DomainConfigSerializationError, DomainConfigParsingError):
                continue

            if config is not None:
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

        config_as_bytes = self._config_to_yaml_bytes(config)
        filename = self._get_filename(config)
        loc = location.append(filename)

        self.storage.write(path=loc, content=config_as_bytes)
