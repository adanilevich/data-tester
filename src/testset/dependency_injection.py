from src.config import Config
from src.dtos.location import LocationDTO
from src.storage import map_storage
from .drivers import CliTestSetManager
from .application.handle_testsets import TestSetCommandHandler


class TestSetDependencyInjector:
    def __init__(self, config: Config):
        self.config = config

        # set storage location and storage engine
        self.storage_location = LocationDTO(
            self.config.DATATESTER_INTERNAL_TESTSET_LOCATION)
        self.storage = map_storage(self.config.DATATESTER_INTERNAL_STORAGE_ENGINE)

    def cli_testset_manager(self) -> CliTestSetManager:
        # Create the core TestSet handler (implements ITestSetHandler)
        testset_handler = TestSetCommandHandler(storage=self.storage)

        return CliTestSetManager(
            testset_handler=testset_handler,
            storage_location=self.storage_location,
        )
