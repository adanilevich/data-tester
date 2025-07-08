from src.domain_config.application import FetchDomainConfigsCommandHandler
from src.domain_config.ports import IFetchDomainConfigsCommandHandler
from src.domain_config.adapters import BasicYamlNamingConventions, YamlFormatter
from src.domain_config.drivers import DomainConfigManager
from src.storage import FileStorage
from src.config import Config


class DomainConfigDependencyInjector:
    """
    Simple dependency injector which returns finders and getters which operate
    with naive naming conventions based on yaml-based domain configs in local or
    cloud blob storage (S3, GCS, Azure Blobs).
    """

    def __init__(self, config: Config | None = None):
        self.config = config or Config()

    def find_domain_configs_command_handler(self) -> IFetchDomainConfigsCommandHandler:
        return FetchDomainConfigsCommandHandler(
            naming_conventions=BasicYamlNamingConventions(),
            storage=FileStorage(),
            serializer=YamlFormatter()
        )

    def domain_config_manager(self) -> DomainConfigManager:
        return DomainConfigManager(
            fetch_command_handler=self.find_domain_configs_command_handler(),
            config=self.config
        )
