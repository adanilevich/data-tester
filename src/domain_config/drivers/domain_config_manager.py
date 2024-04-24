from typing import List


from src.domain_config.ports import (
    IFetchDomainConfigsCommandHandler, FetchDomainConfigsCommand
)
from src.dtos import DomainConfigDTO
from src.config import Config


class DomainConfigManager:

    def __init__(self, handler: IFetchDomainConfigsCommandHandler):
        self.handler = handler

    def find(self, location: str | None = None) -> List[DomainConfigDTO]:

        if location is None:
            location = Config().DATATESTER_DOMAIN_CONFIGS_LOCATION
            if location is None:
                raise ValueError("DOMAIN_CONFIGS_LOCATION undefined")

        command = FetchDomainConfigsCommand(location=location)

        try:
            configs = self.handler.fetch(command=command)
        except Exception:
            configs = []

        return configs
