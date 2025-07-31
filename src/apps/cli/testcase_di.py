from typing import List

from src.infrastructure.notifier import map_notifier
from src.config import Config
from src.infrastructure_ports import IBackendFactory, IStorageFactory, INotifier
from src.infrastructure.backend import map_platform
from src.infrastructure.storage import StorageFactory, FormatterFactory
from src.dtos.location import LocationDTO

from src.drivers.cli import CliTestRunManager
from src.domain import TestRunCommandHandler


class TestCaseDependencyInjector:
    def __init__(self, config: Config):
        self.config = config
        self.notifiers: List[INotifier] = []
        self.data_platform_factory: IBackendFactory
        self.storage_factory: IStorageFactory
        self.storage_location: LocationDTO

        # set notifiers
        for notifier in self.config.DATATESTER_NOTIFIERS:
            self.notifiers.append(map_notifier(notifier))
        self.data_platform_factory = map_platform(self.config.DATATESTER_DATA_PLATFORM)

        # create formatter factory and storage factory
        formatter_factory = FormatterFactory()
        self.storage_factory = StorageFactory(formatter_factory)

        # set storage location
        self.storage_location = LocationDTO(
            self.config.DATATESTER_INTERNAL_TESTRUN_LOCATION
        )

    def cli_testrun_manager(self) -> CliTestRunManager:
        return CliTestRunManager(
            handler=TestRunCommandHandler(
                backend_factory=self.data_platform_factory,
                notifiers=self.notifiers,
                storage_factory=self.storage_factory,
            ),
            storage_location=self.storage_location,
        )
