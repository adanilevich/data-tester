from src.domain_config.application import (
    FetchDomainConfigsCommandHandler, SaveDomainConfigCommandHandler)
from src.domain_config.drivers.cli_domain_config_manager import CLIDomainConfigManager
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


    def domain_config_manager(self) -> CLIDomainConfigManager:
        storage = FileStorage(config=self.config)
        fetch_command_handler = FetchDomainConfigsCommandHandler(storage=storage)
        save_command_handler = SaveDomainConfigCommandHandler(storage=storage)

        return CLIDomainConfigManager(
            fetch_command_handler=fetch_command_handler,
            save_command_handler=save_command_handler,
            config=self.config
        )
