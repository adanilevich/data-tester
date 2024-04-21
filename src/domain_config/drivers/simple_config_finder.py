from typing import List
import os

from src.domain_config.ports import (
    IFetchDomainConfigsCommandHandler, FetchDomainConfigsCommand
)
from src.dtos import DomainConfigDTO


class SimpleConfigFinder:

    def __init__(self, handler: IFetchDomainConfigsCommandHandler):
        self.handler = handler

    def _get_locations_from_envs(self) -> List[str]:

        locations: List[str]
        locations_as_string: str | None = os.environ[
            "DATATESTER_DOMAIN_CONFIG_LOCATIONS"]

        if locations_as_string is None:
            location: str | None = os.environ["DATATESTER_DOMAIN_CONFIG_LOCATION"]
            if location is None:
                raise ValueError("Can't find DATATESTER_DOMAIN_CONFIG_LOCATION in ENV")
            else:
                locations = [location.strip()]
        else:
            locations_raw = locations_as_string.split(",")
            locations = [loc.strip() for loc in locations_raw]

        return locations

    def find(self, locations: List[str] | None = None) -> List[DomainConfigDTO]:

        if locations is None:
            locations = self._get_locations_from_envs()

        command = FetchDomainConfigsCommand(locations=locations)

        try:
            configs = self.handler.fetch(command=command)
        except Exception:
            configs = []

        return configs
