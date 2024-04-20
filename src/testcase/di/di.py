"""
A simple self-built replacement for a proper dependency injector.
This class will instantiate Backends, Notifiers, Handlers based on ENV vars.
"""
import os
from typing import List

from src.testcase.adapters.data_platforms import (
    DummyPlatformFactory, DemoDataPlatformFactory
)
from src.testcase.adapters.notifiers import InMemoryNotifier, StdoutNotifier
from src.testcase.application.run_testcases import RunTestCasesCommandHandler
from src.testcase.ports import (
    IRunTestCasesCommandHandler, IDataPlatformFactory, INotifier
)


class DependencyInjector:

    def __init__(self):
        self.datatester_env = os.environ.get("DATATESTER_ENV", None)

    def backend_factory(self) -> IDataPlatformFactory:
        if self.datatester_env == "DUMMY":
            return DummyPlatformFactory()
        elif self.datatester_env == "DEMO":
            return DemoDataPlatformFactory()
        else:
            raise NotImplementedError(f"Unknown DATATESTER_ENV: {self.datatester_env}")

    @staticmethod
    def notifiers() -> List[INotifier]:
        return [InMemoryNotifier(), StdoutNotifier()]

    def run_testcases_command_handler(self) -> IRunTestCasesCommandHandler:
        notifiers = self.notifiers()
        backend_factory = self.backend_factory()
        handler = RunTestCasesCommandHandler(
            backend_factory=backend_factory, notifiers=notifiers)
        return handler
