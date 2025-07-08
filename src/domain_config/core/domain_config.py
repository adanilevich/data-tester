from typing import List, Dict, Any
from src.domain_config.ports import (
    INamingConventions, IDomainConfigFormatter, IStorage, StorageError,
    DomainConfigFormatterError
)
from src.dtos import DomainConfigDTO


class DomainConfigAlreadyExistsError(Exception):
    """"""


# TODO: simplify this module:
# 1. get all relevant domains from application config.
# 2. get domain config location from application config. "LOCAL" would mean that
# domain configs are stored in the local file system.
# 3. load all domain configs from the location.
# 4. implement load and save interfaces and implementations for the domain configs.
class DomainConfig:

    def __init__(
        self,
        naming_conventions: INamingConventions,
        storage: IStorage,
        formatter: IDomainConfigFormatter
    ):
        self.naming_conventions: INamingConventions = naming_conventions
        self.storage: IStorage = storage
        self.formatter: IDomainConfigFormatter = formatter

    def _find_candidates(self, location: str) -> List[str]:
        """Gets valid, name-matching objects from location"""

        try:
            objects = self.storage.find(path=location)
        except StorageError:
            objects = []

        candidates = list(filter(self.naming_conventions.match, objects))

        return candidates

    def fetch_configs(self, location: str) -> Dict[str, DomainConfigDTO]:
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

        if not isinstance(location, str):
            raise ValueError("Provide a string-valued location of domain configs")

        candidates: List[str] = []
        found_domain_configs: Dict[str, DomainConfigDTO] = {}

        candidates = self._find_candidates(location)

        for candidate in candidates:
            config_as_dict: Dict[str, Any] | None = None
            config: DomainConfigDTO | None = None

            try:
                config_as_bytes = self.storage.read(path=candidate)
                config_as_dict = self.formatter.deserialize(config_as_bytes)
            except (StorageError, DomainConfigFormatterError):
                continue
            try:
                config = DomainConfigDTO.from_dict(config_as_dict)
            except Exception:
                continue

            if config is not None:
                if config.domain in found_domain_configs:
                    msg = f"Domain config for {config.domain} already exists"
                    raise DomainConfigAlreadyExistsError(msg)
                else:
                    found_domain_configs[config.domain] = config

        return found_domain_configs
