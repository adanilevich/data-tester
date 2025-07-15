from src.domain_config.application import (
    FetchDomainConfigsCommandHandler, SaveDomainConfigCommandHandler)
from src.domain_config.drivers.cli_domain_config_manager import CLIDomainConfigManager
from src.storage import FileStorage, DictStorage
from src.config import Config
from src.dtos.location import LocationDTO, Store


class DomainConfigDependencyInjector:
    """
    Simple dependency injector which returns finders and getters which operate
    with naive naming conventions based on yaml-based domain configs in local or
    cloud blob storage (S3, GCS, Azure Blobs).
    """

    def __init__(self, config: Config):
        self.config = config

    def domain_config_manager(self) -> CLIDomainConfigManager:

        if self.config.DATATESTER_DOMAIN_CONFIGS_LOCATION is None:
            raise ValueError("DATATESTER_DOMAIN_CONFIGS_LOCATION is not set")
        domain_config_location = LocationDTO(
            self.config.DATATESTER_DOMAIN_CONFIGS_LOCATION)

        if domain_config_location.store in [Store.GCS, Store.LOCAL, Store.MEMORY]:
            storage = FileStorage(config=self.config)
        elif domain_config_location.store == Store.DICT:
            storage = DictStorage() # type: ignore

        if self.config.DATATESTER_ENV in ["DUMMY", "LOCAL"]:
            storage = DictStorage() # type: ignore

        fetch_command_handler = FetchDomainConfigsCommandHandler(storage=storage)
        save_command_handler = SaveDomainConfigCommandHandler(storage=storage)

        return CLIDomainConfigManager(
            fetch_command_handler=fetch_command_handler,
            save_command_handler=save_command_handler,
            config=self.config
        )
