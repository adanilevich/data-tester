from typing import List
from src.domain_config.ports import (
    INamingConventions, ISerializer, IStorage, StorageError, SerializerError
)
from src.dtos import DomainConfigDTO


class DomainConfigManager:

    def __init__(
        self,
        naming_conventions: INamingConventions,
        storage: IStorage,
        serializer: ISerializer
    ):
        self.naming_conventions: INamingConventions = naming_conventions
        self.storage: IStorage = storage
        self.serializer: ISerializer = serializer

        # we translate serializer options based on serialization mode
        # most of the times, domain configs are read and written as text files, e.g. yaml
        if self.serializer.open_mode == "r":
            self.read = self.storage.read_text
            self.deserialize = self.serializer.from_string
        elif self.serializer.open_mode == "b":
            self.read = self.storage.read_bytes  # type: ignore
            self.serialize = self.serializer.from_bytes
        else:
            msg = f"Unknown mode: {self.serializer.open_mode}. Known: r/b"
            raise ValueError(msg)

    def _find_candidates(self, location: str) -> List[str]:
        """Gets valid, name-matching objects from location"""

        try:
            objects = self.storage.find(path=location)
        except Exception:
            objects = []

        candidates = list(filter(self.naming_conventions.match, objects))

        return candidates

    def fetch_configs(self, locations: List[str]) -> List[DomainConfigDTO]:

        if not isinstance(locations, list):
            raise ValueError("Provide list of domain config locations")

        candidates: List[str] = []
        results: List[DomainConfigDTO] = []

        for location in locations:
            candidates += self._find_candidates(location)

        for candidate in set(candidates):

            try:
                dict_ = self.deserialize(self.read(candidate))
            except (StorageError, SerializerError):
                continue

            try:
                conf = DomainConfigDTO.from_dict(dict_)
                conf.storage_location = candidate  # overwrite location by found location
                results.append(conf)
            except Exception:
                continue

        return results
