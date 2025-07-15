from typing import List

from src.testcase.drivers import CliTestCaseRunner
from src.testcase.application import RunTestCasesCommandHandler
from src.notifier import InMemoryNotifier, StdoutNotifier
from src.testcase.ports import INotifier
from src.config import Config
from src.data_platform import DemoDataPlatformFactory, DummyPlatformFactory


class TestCaseDependencyInjector:
    def __init__(self, config: Config):
        self.config = config

    def testcase_runner(self) -> CliTestCaseRunner:

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

        return CliTestCaseRunner(
            handler=RunTestCasesCommandHandler(
                backend_factory=data_platform_factory,
                notifiers=notifiers
            )
        )
