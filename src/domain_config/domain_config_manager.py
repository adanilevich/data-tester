from typing import List
from src.domain_config.ports import INamingConventions, IParser, IStorage
from src.dtos import DomainConfigDTO


class DomainConfigManager:

    def __init__(
        self,
        naming_conventions: INamingConventions,
        storage: IStorage,
        parser: IParser
    ):
        self.naming_conventions: INamingConventions = naming_conventions
        self.storage: IStorage = storage
        self.parser: IParser = parser

    def find_in_location(self, location: str) -> List[DomainConfigDTO]:

        if not self.storage.is_valid_location(location=location):
            return []

        results: List[DomainConfigDTO] = []
        candidates: List[str] = self.storage.list_objects(location=location)
        for candidate in candidates:
            if not self.naming_conventions.match(candidate):
                continue
            else:
                content = self.storage.load_object(candidate) or ""
                domain_config_as_dict = self.parser.parse(content=content)
                try:
                    conf = DomainConfigDTO.from_dict(domain_config_as_dict)
                    results.append(conf)
                except Exception:
                    continue

        return results

    def find(self, locations: List[str]) -> List[DomainConfigDTO]:

        found_configs: List[DomainConfigDTO] = []
        for location in locations:
            found_configs += self.find_in_location(location=location)

        return found_configs
