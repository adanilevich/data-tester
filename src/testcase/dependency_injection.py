from typing import List

from src.notifier import map_notifier
from src.config import Config
from src.data_platform import map_platform
from src.testcase.ports import IDataPlatformFactory
from src.storage import map_storage, IStorage
from src.dtos.location import LocationDTO

from .drivers import CliTestRunManager
from .application import TestRunCommandHandler
from .ports import INotifier


class TestCaseDependencyInjector:
    def __init__(self, config: Config):
        self.config = config
        self.notifiers: List[INotifier] = []
        self.data_platform_factory: IDataPlatformFactory
        self.storage: IStorage
        self.storage_location: LocationDTO

        # set notifiers
        for notifier in self.config.DATATESTER_NOTIFIERS:
            self.notifiers.append(map_notifier(notifier))
        self.data_platform_factory = map_platform(self.config.DATATESTER_DATA_PLATFORM)

        # set storage
        self.storage = map_storage(self.config.DATATESTER_INTERNAL_STORAGE_ENGINE)

        # set storage location
        self.storage_location = LocationDTO(
            self.config.DATATESTER_INTERNAL_TESTRUN_LOCATION)

    def cli_testrun_manager(self) -> CliTestRunManager:

        return CliTestRunManager(
            handler=TestRunCommandHandler(
                backend_factory=self.data_platform_factory,
                notifiers=self.notifiers,
                storage=self.storage,
            ),
            storage_location=self.storage_location,
        )
