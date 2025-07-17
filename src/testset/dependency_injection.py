from src.config import Config
from src.dtos.location import LocationDTO
from src.storage.file_storage import FileStorage
from src.storage.dict_storage import DictStorage
from src.storage.i_storage import IStorage
from .drivers import CliTestSetManager
from .application.handle_testsets import TestSetCommandHandler


class CliTestSetDependencyInjector:
    def __init__(self, config: Config):
        self.config = config

        # Extract relevant configuration values
        self.internal_storage_engine = config.INTERNAL_STORAGE_ENGINE
        if self.internal_storage_engine is None:
            raise ValueError("INTERNAL_STORAGE_ENGINE is not set")

        if config.INTERNAL_TESTSET_LOCATION is None:
            raise ValueError("INTERNAL_TESTSET_LOCATION is not set")
        self.storage_location = LocationDTO(config.INTERNAL_TESTSET_LOCATION)

        self.storage: IStorage
        if self.internal_storage_engine in ["LOCAL", "GCS", "MEMORY"]:
            self.storage = FileStorage(config=self.config)
        elif self.internal_storage_engine == "DICT":
            self.storage = DictStorage()
        else:
            raise ValueError(
                f"INTERNAL_STORAGE_ENGINE {self.internal_storage_engine} is not supported"
            )

    def testset_manager(self) -> CliTestSetManager:
        # Create the core TestSet handler (implements ITestSetHandler)
        testset_handler = TestSetCommandHandler(storage=self.storage)

        return CliTestSetManager(
            testset_handler=testset_handler,
            storage_location=self.storage_location,
        )
