from src.domain_config.application import FindDomainConfigsCommandHandler
from src.domain_config.ports import IFindDomainConfigsCommandHandler
from src.domain_config.adapters import BasicYamlNamingConventions, FileStorage, YamlParser


class DependencyInjector:
    """
    Simple dependency injector which returns finders and getters which operate
    with naive naming conventions based on yaml-based domain configs in local or
    cloud storage.
    """

    def find_domain_configs_command_handler(self) -> IFindDomainConfigsCommandHandler:
        return FindDomainConfigsCommandHandler(
            naming_conventions=BasicYamlNamingConventions(),
            storage=FileStorage(),
            parser=YamlParser()
        )
