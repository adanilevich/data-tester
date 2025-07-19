from src.domain_config.application import DomainConfigHandler
from src.domain_config.drivers.cli_domain_config_manager import CLIDomainConfigManager
from src.config import Config
from src.dtos.location import LocationDTO
from src.storage import IStorage, map_storage


class DomainConfigDependencyInjector:
    """
    Simple dependency injector which returns finders and getters which operate
    with naive naming conventions based on yaml-based domain configs in local or
    cloud blob storage (S3, GCS, Azure Blobs).
    """
    def __init__(self, config: Config):
        self.config = config
        self.domain_config_location: LocationDTO
        self.storage: IStorage

        # extract domain config location from config
        if self.config.DATATESTER_DOMAIN_CONFIGS_LOCATION is None:
            raise ValueError("DATATESTER_DOMAIN_CONFIGS_LOCATION is not set")
        self.domain_config_location = LocationDTO(
            self.config.DATATESTER_DOMAIN_CONFIGS_LOCATION
        )

        # extract storage backend type from config
        self.storage = map_storage(self.domain_config_location.store.value.upper())

    def cli_domain_config_manager(self) -> CLIDomainConfigManager:

        domain_config_handler = DomainConfigHandler(storage=self.storage)
        return CLIDomainConfigManager(
            domain_config_handler=domain_config_handler,
            domain_config_location=self.domain_config_location
        )
