# flake8: noqa
from typing import List, Dict, Callable
from datetime import datetime
from uuid import uuid4

from src.dtos import (
    TestRunDTO,
    TestDefinitionDTO,
    TestType,
    TestResult,
    TestCaseDTO,
    TestStatus,
    LocationDTO,
    StorageObject,
)
from src.infrastructure_ports import IBackend, INotifier, IStorageFactory

# we need to import all subclasses of TestCase such that they are registered
# and can be created via TestCaseFactory.create.
# This is done in testcase.__init__.py which is imported here
from .testcases import (
    AbstractTestCase,
    SchemaTestCase,
    CompareTestCase,
    RowCountTestCase,
    DummyExceptionTestCase,
    DummyNokTestCase,
    DummyOkTestCase,
)


class TestCaseUnknownError(NotImplementedError):
    __test__ = False
    pass


# TODO: implement notifications
class TestRun:
    known_testtypes: Dict[TestType, Callable] = dict()

    def __init__(
        self,
        testrun: TestRunDTO,
        backend: IBackend,
        notifiers: List[INotifier],
        storage_factory: IStorageFactory,
        storage_location: LocationDTO,
    ):
        self.testrun = testrun
        self.backend = backend
        self.notifiers = notifiers
        self.storage_factory = storage_factory
        self.storage_location = storage_location

        # set dynamic fields
        self.testrun.start_ts = datetime.now()
        self.testrun.end_ts = None
        self.testrun.result = TestResult.NA

        # set result fields
        self.testcase_results: List[TestCaseDTO] = []
        self.testrun.status = TestStatus.INITIATED

        # persist initial state
        self.persist()

    def execute(self) -> TestRunDTO:
        """
        Executes all testcases in the testrun.
        """

        self.testrun.status = TestStatus.EXECUTING
        self.persist()

        for definition in self.testrun.testdefinitions:
            try:
                testcase = self._create_testcase(definition)
                result = testcase.execute()
            except TestCaseUnknownError:
                result = TestCaseDTO(
                    testcase_id=uuid4(),
                    result=TestResult.NA,
                    summary=f"Test type {definition.testtype} unknown!",
                    facts=[],
                    details=[],
                    status=TestStatus.ERROR,
                    start_ts=datetime.now(),
                    end_ts=datetime.now(),
                    testobject=definition.testobject,
                    testrun_id=self.testrun.testrun_id,
                    testset_id=self.testrun.testset_id,
                    labels=definition.labels,
                    diff=dict(),
                    testtype=definition.testtype,
                    specifications=definition.specs,
                    domain_config=definition.domain_config,
                    domain=definition.testobject.domain,
                    stage=definition.testobject.stage,
                    instance=definition.testobject.instance,
                )

            self.testcase_results.append(result)

        # testrun result is only OK if all testcases are OK
        self.testrun.result = TestResult.OK
        for result in self.testcase_results:
            if result.result != TestResult.OK:
                self.testrun.result = TestResult.NA

        self.testrun.status = TestStatus.FINISHED
        self.testrun.end_ts = datetime.now()

        self.persist()

        return self.to_dto()

    def _create_testcase(self, definition: TestDefinitionDTO) -> AbstractTestCase:
        """
        Creates a testcase object (subclass instance of TestCase) based on class attribute
        'ttype' - the specified test type must be implemented as subclass of TestCase.
        """

        match definition.testtype:
            case TestType.SCHEMA:
                return SchemaTestCase(
                    definition=definition,
                    backend=self.backend,
                    notifiers=self.notifiers
                )
            case TestType.COMPARE:
                return CompareTestCase(
                    definition=definition,
                    backend=self.backend,
                    notifiers=self.notifiers,
                )
            case TestType.ROWCOUNT:
                return RowCountTestCase(
                    definition=definition,
                    backend=self.backend,
                    notifiers=self.notifiers,
                )
            case TestType.DUMMY_OK:
                return DummyOkTestCase(
                    definition=definition,
                    backend=self.backend,
                    notifiers=self.notifiers,
                )
            case TestType.DUMMY_NOK:
                return DummyNokTestCase(
                    definition=definition,
                    backend=self.backend,
                    notifiers=self.notifiers,
                )
            case TestType.DUMMY_EXCEPTION:
                return DummyExceptionTestCase(
                    definition=definition,
                    backend=self.backend,
                    notifiers=self.notifiers,
                )
            case _:
                raise TestCaseUnknownError(f"Test type {definition.testtype} unknown!")

    def to_dto(self) -> TestRunDTO:
        return TestRunDTO(
            testrun_id=self.testrun.testrun_id,
            testset_id=self.testrun.testset_id,
            labels=self.testrun.labels,
            start_ts=self.testrun.start_ts,
            end_ts=self.testrun.end_ts or datetime.now(),
            result=self.testrun.result,
            testcase_results=self.testcase_results,
            testdefinitions=self.testrun.testdefinitions,
            stage=self.testrun.stage,
            instance=self.testrun.instance,
            domain=self.testrun.domain,
            status=self.testrun.status,
            testset_name=self.testrun.testset_name,
            domain_config=self.testrun.domain_config,
        )

    def persist(self, dto: TestRunDTO | None = None) -> None:
        if dto is None:
            dto = self.to_dto()

        storage = self.storage_factory.get_storage(self.storage_location)
        storage.write(dto, StorageObject.TESTRUN, self.storage_location)
