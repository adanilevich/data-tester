# flake8: noqa
from typing import Dict, List, Callable
from uuid import UUID
from src.dtos import TestObjectDTO, DomainConfigDTO, SpecificationDTO, TestType
from src.testcase.ports import IDataPlatform, INotifier

# we need to import all subclasses of TestCase such that they are registered
# and can be created via TestCaseFactory.create.
# This is done in testcase.__init__.py which is imported here
from src.testcase.core.testcases import (
    AbstractTestCase,
    SchemaTestCase,
    DummyExceptionTestCase,
    DummyNokTestCase,
    DummyOkTestCase,
    CompareSampleTestCase,
    RowCountTestCase,
)


class TestCaseUnknownError(NotImplementedError):
    __test__ = False
    pass


class TestCaseFactory:
    """Registers and creates subclasses of TestCase based on requested ttype"""

    # type: ignore
    known_testtypes: Dict[TestType, Callable] = dict()

    @classmethod
    def create(
        cls,
        ttype: TestType,
        testobject: TestObjectDTO,
        specs: List[SpecificationDTO],
        domain_config: DomainConfigDTO,
        testrun_id: UUID,
        backend: IDataPlatform,
        notifiers: List[INotifier],
    ) -> AbstractTestCase:
        """
        Creates a testcase object (subclass instance of TestCase) based on class attribute
        'ttype' - the specified test type must be implemented as subclass of TestCase.
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
                testrun_id=testrun_id,
                backend=backend,
                notifiers=notifiers,
            )
            return testcase
