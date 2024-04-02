# flake8: noqa
# type: ignore
from typing import Dict, List
from src.testcase.testcases.testcase import TestCase
from src.testcase.dtos import TestObjectDTO, SpecificationDTO, DomainConfigDTO
from src.testcase.driven_ports.backend_interface import IBackend
from src.testcase.driven_ports.notifier_interface import INotifier

# we need tp explicitely import all modules where subclasses of TestCase are defined
# such that they are registered
# noinspection PyUnresolvedReferences
from src.testcase.testcases import (
    dummy_ok_testcase,
    dummy_nok_testcase,
    dummy_exception_testcase
)


class TestCaseFactory:
    """Registers and creates subclasses of TestCase based on requested ttype"""

    known_testtypes: Dict[str, type(TestCase)] = dict()

    @classmethod
    def create(cls, ttype: str, testobject: TestObjectDTO, specs: List[SpecificationDTO],
               domain_config: DomainConfigDTO, run_id: str,
               backend: IBackend, notifiers: List[INotifier]) -> TestCase:
        """
        Creates a testcase object (subclass instance of TestCase) based on class attribute
        'type' - the specified test type must be implemented as subclass of TestCase.
        """

        # populate known_testtypes with subclasses of TestCase
        for cls_ in TestCase.__subclasses__():
            cls.known_testtypes.update({cls_.ttype: cls_})

        if ttype not in cls.known_testtypes:
            raise NotImplementedError(f"Testcase {ttype} is not implemented!")
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
