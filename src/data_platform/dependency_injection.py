"""
A simple self-built replacement for a dependency injector.
This class will instantiate Backends, Notifiers, Handlers based on ENV vars.
"""
from typing import List

from src.data_platform import (
    DummyPlatformFactory, DemoDataPlatformFactory
)
from src.notifier import InMemoryNotifier, StdoutNotifier
from src.testcase.application.run_testcases import RunTestCasesCommandHandler
from src.testcase.ports import (
    IRunTestCasesCommandHandler, IDataPlatformFactory, INotifier
)
from src.config import Config


class DataPlatformDependencyInjector:

    def __init__(self):
        self.config = Config()

    def backend_factory(self) -> IDataPlatformFactory:
        if self.config.DATATESTER_ENV == "DUMMY":
            return DummyPlatformFactory()
        elif self.config.DATATESTER_ENV == "DEMO":
            return DemoDataPlatformFactory()
        else:
            msg = f"Unknown DATATESTER_ENV: {self.config.DATATESTER_ENV}"
            raise NotImplementedError(msg)

    @staticmethod
    def notifiers() -> List[INotifier]:
        return [InMemoryNotifier(), StdoutNotifier()]

    def run_testcases_command_handler(self) -> IRunTestCasesCommandHandler:
        notifiers = self.notifiers()
        backend_factory = self.backend_factory()
        handler = RunTestCasesCommandHandler(
            backend_factory=backend_factory, notifiers=notifiers)
        return handler
