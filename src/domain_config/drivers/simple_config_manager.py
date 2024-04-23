from typing import List
import os

from src.domain_config.ports import (
    IFetchDomainConfigsCommandHandler, FetchDomainConfigsCommand
)
from src.dtos import DomainConfigDTO


class SimpleConfigManager:

    def __init__(self, handler: IFetchDomainConfigsCommandHandler):
        self.handler = handler

    def _get_domain_config_location_from_envs(self) -> str:

        location = os.environ.get("DATATESTER_DOMAIN_CONFIGS_LOCATION")

        if location is None:
            raise ValueError("Can't find DATATESTER_DOMAIN_CONFIGS_LOCATION in ENV")

        return location.strip()

    def find(self, location: str | None = None) -> List[DomainConfigDTO]:

        if location is None:
            location = self._get_domain_config_location_from_envs()

        command = FetchDomainConfigsCommand(location=location)

        try:
            configs = self.handler.fetch(command=command)
        except Exception:
            configs = []

        return configs
