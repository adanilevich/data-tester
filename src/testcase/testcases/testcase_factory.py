# flake8: noqa
from typing import Dict, List, Callable
from src.testcase.testcases.abstract_testcase import AbstractTestCase
from src.testcase.dtos import TestObjectDTO, SpecificationDTO, DomainConfigDTO
from src.testcase.driven_ports.i_backend import IBackend
from src.testcase.driven_ports.i_notifier import INotifier

# we need tp explicitely import all modules where subclasses of TestCase are defined
# such that they are registered and can be created
# noinspection PyUnresolvedReferences
from src.testcase.testcases import (
    dummy_ok,
    dummy_nok,
    dummy_exception
)


class TestCaseUnknownError(NotImplementedError):
    __test__ = False
    pass


class TestCaseFactory:
    """Registers and creates subclasses of TestCase based on requested ttype"""

    # type: ignore
    known_testtypes: Dict[str, Callable] = dict()

    @classmethod
    def create(cls, ttype: str, testobject: TestObjectDTO, specs: List[SpecificationDTO],
               domain_config: DomainConfigDTO, run_id: str,
               backend: IBackend, notifiers: List[INotifier]) -> AbstractTestCase:
        """
        Creates a testcase object (subclass instance of TestCase) based on class attribute
        'type' - the specified test type must be implemented as subclass of TestCase.
        """

        # populate known_testtypes with subclasses of TestCase
        for cls_ in AbstractTestCase.__subclasses__():
            cls.known_testtypes.update({cls_.ttype: cls_})

        if ttype not in cls.known_testtypes:
            raise TestCaseUnknownError(f"Testcase {ttype} is not implemented!")
        else:
            testcase = cls.known_testtypes[ttype](
                testobject=testobject,
                specs=specs,
                domain_config=domain_config,
                run_id=run_id,
                backend=backend,
                notifiers=notifiers,
            )
            return testcase
