from src.domain import DomainConfigHandler
from src.drivers.cli import CliDomainConfigManager
from src.config import Config, ConfigError
from src.dtos.location import LocationDTO
from src.infrastructure_ports import IStorageFactory
from src.infrastructure.storage import StorageFactory, FormatterFactory


class DomainConfigDependencyInjector:
    """
    Simple dependency injector which returns finders and getters which operate
    with naive naming conventions based on yaml-based domain configs in local or
    cloud blob storage (S3, GCS, Azure Blobs).
    """

    def __init__(self, config: Config):
        self.config = config
        self.domain_config_location: LocationDTO
        self.storage_factory: IStorageFactory

        # extract domain config location from config
        if self.config.DATATESTER_DOMAIN_CONFIGS_LOCATION is None:
            raise ConfigError("DATATESTER_DOMAIN_CONFIGS_LOCATION is not set")
        self.domain_config_location = LocationDTO(
            self.config.DATATESTER_DOMAIN_CONFIGS_LOCATION
        )

        # create formatter factory and storage factory
        formatter_factory = FormatterFactory()
        self.storage_factory = StorageFactory(formatter_factory)

    def cli_domain_config_manager(self) -> CliDomainConfigManager:
        domain_config_handler = DomainConfigHandler(storage_factory=self.storage_factory)
        return CliDomainConfigManager(
            domain_config_handler=domain_config_handler,
            domain_config_location=self.domain_config_location,
        )
