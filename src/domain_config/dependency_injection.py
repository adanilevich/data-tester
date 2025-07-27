from src.domain_config.application import DomainConfigHandler
from src.domain_config.drivers.cli_domain_config_manager import CLIDomainConfigManager
from src.config import Config
from src.dtos.location import LocationDTO
from src.storage.i_storage_factory import IStorageFactory
from src.storage.storage_factory import StorageFactory
from src.storage.formatter_factory import FormatterFactory


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
            raise ValueError("DATATESTER_DOMAIN_CONFIGS_LOCATION is not set")
        self.domain_config_location = LocationDTO(
            self.config.DATATESTER_DOMAIN_CONFIGS_LOCATION
        )

        # create formatter factory and storage factory
        formatter_factory = FormatterFactory()
        self.storage_factory = StorageFactory(self.config, formatter_factory)

    def cli_domain_config_manager(self) -> CLIDomainConfigManager:
        domain_config_handler = DomainConfigHandler(storage_factory=self.storage_factory)
        return CLIDomainConfigManager(
            domain_config_handler=domain_config_handler,
            domain_config_location=self.domain_config_location
        )
