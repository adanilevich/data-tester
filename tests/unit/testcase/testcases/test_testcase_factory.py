import pytest
from uuid import uuid4

from src.dtos import (
    TestObjectDTO,
    SpecificationDTO,
    TestType,
    SpecificationType,
    TestCaseDefinitionDTO,
)
from src.testcase.core.testcases import TestCaseFactory, TestCaseUnknownError


class TestTestCaseFactory:
    testobject = TestObjectDTO(name="to", domain="dom", stage="proj", instance="inst")
    specifications = [
        SpecificationDTO(
            spec_type=SpecificationType.SCHEMA, location="loc", testobject="to"
        ),
        SpecificationDTO(
            spec_type=SpecificationType.ROWCOUNT_SQL, location="loc", testobject="to"
        ),
    ]

    def test_cant_create_unknown_testcase(
        self, in_memory_notifier, dummy_backend, domain_config
    ):
        definition = TestCaseDefinitionDTO(
            testobject=self.testobject,
            testtype=TestType.UNKNOWN,
            specs=self.specifications,
            domain_config=domain_config,
            testrun_id=uuid4(),
        )

        with pytest.raises(TestCaseUnknownError) as err:
            TestCaseFactory.create(
                definition=definition,
                backend=dummy_backend,
                notifiers=[in_memory_notifier],
            )

        assert "Test 'TestType.UNKNOWN' unknown!" in str(err)

    def test_creating_testcases(self, dummy_backend, in_memory_notifier, domain_config):
        definition = TestCaseDefinitionDTO(
            testobject=self.testobject,
            testtype=TestType.DUMMY_OK,
            specs=self.specifications,
            domain_config=domain_config,
            testrun_id=uuid4(),
        )

        testcase = TestCaseFactory.create(
            definition=definition,
            backend=dummy_backend,
            notifiers=[in_memory_notifier, in_memory_notifier],
        )

        assert testcase.ttype == TestType.DUMMY_OK
        assert testcase.status.value == "INITIATED"
        assert testcase.result.value == "N/A"
        for notifier in testcase.notifiers:
            assert isinstance(notifier, type(in_memory_notifier))
            assert "Initiating testcase" in notifier.notifications[0]
