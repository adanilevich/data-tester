from src.domain_config.application import FetchDomainConfigsCommandHandler
from src.domain_config.ports import IFetchDomainConfigsCommandHandler
from src.domain_config.adapters import (
    BasicYamlNamingConventions, FileStorage, YamlSerializer
)


class DependencyInjector:
    """
    Simple dependency injector which returns finders and getters which operate
    with naive naming conventions based on yaml-based domain configs in local or
    cloud storage.
    """

    def find_domain_configs_command_handler(self) -> IFetchDomainConfigsCommandHandler:
        return FetchDomainConfigsCommandHandler(
            naming_conventions=BasicYamlNamingConventions(),
            storage=FileStorage(),
            serializer=YamlSerializer()
        )
