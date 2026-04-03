from typing import Dict

from src.domain_ports import (
    IDomainConfigHandler,
    FetchDomainConfigsCommand,
)
from src.dtos import DomainConfigDTO


class DomainConfigDriver:
    # TODO: implement save_domain_config and read_domain_config
    def __init__(self, domain_config_handler: IDomainConfigHandler):
        self.domain_config_handler = domain_config_handler

    def list_domain_configs(
        self,
    ) -> Dict[str, DomainConfigDTO]:
        """Fetches domain configs"""

        command = FetchDomainConfigsCommand()
        configs = (
            self.domain_config_handler.fetch_domain_configs(
                command=command
            )
        )

        return configs
