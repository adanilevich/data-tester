from typing import List
from src.domain_config.ports import (
    INamingConventions, IDomainConfigFormatter, IStorage, StorageError,
    DomainConfigFormatterError
)
from src.dtos import DomainConfigDTO

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

    def fetch_configs(self, location: str) -> List[DomainConfigDTO]:
        """
        Parses all files in location which match domain config naming conventions
        and translated contents to a DomainConfigDTO. If parsing or translation to
        DomainConfigDTO fails, file is ignored.
        """

        if not isinstance(location, str):
            raise ValueError("Provide a string-valued location of domain configs")

        candidates: List[str] = []
        results: List[DomainConfigDTO] = []

        candidates = self._find_candidates(location)

        for candidate in candidates:

            try:
                content = self.storage.read(path=candidate)
                dict_ = self.formatter.deserialize(content)
            except (StorageError, DomainConfigFormatterError):
                # since we are parsing all potential candidate files, there might be
                # parsing errors e.g. if a deprecated or wrongly matched file is parsed
                # therefore we ignore unparseable files
                continue

            try:
                conf = DomainConfigDTO.from_dict(dict_)
                results.append(conf)
            except Exception:
                continue

        return results
