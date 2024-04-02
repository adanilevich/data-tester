"""
A simple drop-in replacement for a proper dependency injector.
This class will instantiate Backends, Notifiers, Handlers based on ENV vars.
"""
import os
from typing import List

from src.testcase.driven_adapters.backends.dummy_backend_factory import (
    DummyBackendFactory
)
from src.testcase.driven_adapters.notifiers.in_memory_notifier import InMemoryNotifier
from src.testcase.driven_adapters.notifiers.stdout_notifier import StdoutNotifier
from src.testcase.application.run_testcases import RunTestCasesCommandHandler
from src.testcase.driver_ports.run_testcases_interface import IRunTestCasesCommandHandler
from src.testcase.driven_ports.backend_factory_interface import IBackendFactory
from src.testcase.driven_ports.notifier_interface import INotifier


class DependencyInjector:

    def __init__(self):
        self.datatester_env = os.environ.get("DATATESTER_ENV", None)

    def backend_factory(self) -> IBackendFactory:
        if self.datatester_env == "DUMMY":
            return DummyBackendFactory()
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
