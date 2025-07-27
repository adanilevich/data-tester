from src.config import Config
from src.dtos.location import LocationDTO
from src.storage import StorageFactory, FormatterFactory
from .drivers import CliTestSetManager
from .application.handle_testsets import TestSetCommandHandler


class TestSetDependencyInjector:
    def __init__(self, config: Config):
        self.config = config

        # set storage location and storage factory
        self.storage_location = LocationDTO(
            self.config.DATATESTER_INTERNAL_TESTSET_LOCATION)
        storage_formatter_factory = FormatterFactory()
        self.storage_factory = StorageFactory(self.config, storage_formatter_factory)

    def cli_testset_manager(self) -> CliTestSetManager:
        # Create the core TestSet handler (implements ITestSetHandler)
        testset_handler = TestSetCommandHandler(storage_factory=self.storage_factory)

        return CliTestSetManager(
            testset_handler=testset_handler,
            storage_location=self.storage_location,
        )
