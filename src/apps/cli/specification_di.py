from src.config import Config
from src.infrastructure.storage import (
    StorageFactory,
    FormatterFactory as StorageFormatterFactory,
)

from src.domain.specification import (
    NamingConventionsFactory,
    FormatterFactory,
    SpecCommandHandler,
)
from src.drivers.cli import CliSpecManager


class SpecDependencyInjector:
    """
    Dependency injector for the specification package.
    Reads application config and creates a CliSpecManager instance.
    """

    def __init__(self, config: Config):
        self.config = config
        # Create storage formatter factory - this is not used for specifications,
        # but it is needed to create the storage factory
        storage_formatter_factory = StorageFormatterFactory()
        self.storage_factory = StorageFactory(storage_formatter_factory)
        self.naming_conventions_factory = NamingConventionsFactory()
        self.formatter_factory = FormatterFactory()

    def cli_spec_manager(self):
        """
        Create and return a CliSpecManager instance with all dependencies injected.
        """
        command_handler = SpecCommandHandler(
            storage_factory=self.storage_factory,
            naming_conventions_factory=self.naming_conventions_factory,
            formatter_factory=self.formatter_factory,
        )
        spec_manager = CliSpecManager(spec_command_handler=command_handler)

        return spec_manager
