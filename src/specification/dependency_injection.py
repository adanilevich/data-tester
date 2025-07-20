from src.config import Config
from src.storage import map_storage

from .adapters import (
    NamingConventionsFactory,
    FormatterFactory,
    Requirements,
)
from .application import SpecCommandHandler
from .drivers import CliSpecManager


class SpecDependencyInjector:
    """
    Dependency injector for the specification package.
    Reads application config and creates a CliSpecManager instance.
    """
    def __init__(self, config: Config):
        self.config = config
        self.storage = map_storage(config.DATATESTER_USER_STORAGE_ENGINE)
        self.naming_conventions_factory = NamingConventionsFactory()
        self.formatter_factory = FormatterFactory()
        self.requirements = Requirements()

    def cli_spec_manager(self):
        """
        Create and return a CliSpecManager instance with all dependencies injected.
        """
        command_handler = SpecCommandHandler(
            storage=self.storage,
            naming_conventions_factory=self.naming_conventions_factory,
            formatter_factory=self.formatter_factory,
            requirements=self.requirements,
        )
        spec_manager = CliSpecManager(spec_command_handler=command_handler)

        return spec_manager
