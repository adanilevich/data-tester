# flake8: noqa
from typing import Dict, List, Callable
from src.dtos.testcase import TestObjectDTO
from src.dtos.configs import DomainConfigDTO
from src.dtos.specifications import SpecificationDTO
from src.testcase.ports.i_data_platform import IDataPlatform
from src.testcase.ports.i_notifier import INotifier

# we need to import all subclasses of TestCase  such that they are registered
# and can be created. This is done in testcase.__init__.py which is imported here
from src.testcase.testcases import *


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
               backend: IDataPlatform, notifiers: List[INotifier]) -> AbstractTestCase:
        """
        Creates a testcase object (subclass instance of TestCase) based on class attribute
        'type' - the specified test type must be implemented as subclass of TestCase.
        """

        # populate known_testtypes with subclasses of TestCase
        for cls_ in AbstractTestCase.__subclasses__():
            cls.known_testtypes.update({cls_.ttype: cls_})

        if ttype not in cls.known_testtypes:
            msg = f"Test '{ttype}' not implemented! Implemented: {cls.known_testtypes}"
            raise TestCaseUnknownError(msg)
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
