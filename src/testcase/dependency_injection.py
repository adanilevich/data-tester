from typing import List

from src.notifier import InMemoryNotifier, StdoutNotifier
from src.config import Config
from src.data_platform import DemoDataPlatformFactory, DummyPlatformFactory
from src.storage.dict_storage import DictStorage

from .drivers import CliTestRunManager
from .application import TestRunCommandHandler
from .ports import INotifier


class TestCaseDependencyInjector:
    def __init__(self, config: Config):
        self.config = config

    def testrun_manager(self) -> CliTestRunManager:

        # SET NOTIFIERS
        notifiers: List[INotifier] = []
        if self.config.DATATESTER_NOTIFIERS is None:
            raise ValueError("DATATESTER_NOTIFIERS is not set")
        mapper = {
            "IN_MEMORY": InMemoryNotifier,
            "STDOUT": StdoutNotifier,
        }
        for notifier in self.config.DATATESTER_NOTIFIERS:
            notifier_obj = mapper.get(notifier)
            if notifier_obj is None:
                raise ValueError(f"Unknown notifier: {notifier}")
            notifiers.append(notifier_obj())

        # SET DATA PLATFORM FACTORY
        if self.config.DATATESTER_DATA_PLATFORM == "DEMO":
            data_platform_factory = DemoDataPlatformFactory()
        elif self.config.DATATESTER_DATA_PLATFORM == "DUMMY":
            data_platform_factory = DummyPlatformFactory()  # type: ignore
        elif self.config.DATATESTER_ENV == "LOCAL":
            data_platform_factory = DemoDataPlatformFactory()
        elif self.config.DATATESTER_ENV == "DUMMY":
            data_platform_factory = DummyPlatformFactory()  # type: ignore
        else:
            raise ValueError(f"Unknown platform: {self.config.DATATESTER_DATA_PLATFORM}")

        # SET STORAGE
        if self.config.INTERNAL_STORAGE_ENGINE == "DICT":
            storage = DictStorage()
        else:
            msg = f"Unknown storage engine: {self.config.INTERNAL_STORAGE_ENGINE}"
            raise ValueError(msg)

        return CliTestRunManager(
            handler=TestRunCommandHandler(
                backend_factory=data_platform_factory,
                notifiers=notifiers,
                storage=storage,
            ),
            config=self.config,
        )
