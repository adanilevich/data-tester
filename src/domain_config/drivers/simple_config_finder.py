from typing import List, Optional
import os

from src.domain_config.ports import (
    IFindDomainConfigsCommandHandler, FindDomainConfigsCommand
)
from src.dtos import DomainConfigDTO


class SimpleConfigFinder:

    def __init__(self, handler: IFindDomainConfigsCommandHandler):
        self.handler = handler

    def _get_locations_from_envs(self) -> List[str]:

        locations: List[str]
        locations_as_string: str | None = os.environ["DOMAIN_CONFIG_LOCATIONS"]

        if locations_as_string is None:
            location: str | None = os.environ["DOMAIN_CONFIG_LOCATION"]
            if location is None:
                raise ValueError("Can't find DOMAIN_CONFIG_LOCATION in ENV")
            else:
                locations = [location.strip()]
        else:
            locations_raw = locations_as_string.split(",")
            locations = [loc.strip() for loc in locations_raw]

        return locations

    def find(self, locations: Optional[List[str]] = None) -> List[DomainConfigDTO]:

        if locations is None:
            locations = self._get_locations_from_envs()

        command = FindDomainConfigsCommand(locations=locations)

        try:
            configs = self.handler.find(command=command)
        except Exception:
            configs = []

        return configs
