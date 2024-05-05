import pytest
from uuid import uuid4

from src.dtos import TestObjectDTO, SpecificationDTO, TestType
from src.testcase.testcases import TestCaseFactory, TestCaseUnknownError


class TestTestCaseFactory:
    testobject = TestObjectDTO(name="to", domain="dom", stage="proj", instance="inst")
    specifications = [
        SpecificationDTO(type="schema", location="loc", testobject="to"),
        SpecificationDTO(type="sql", location="loc", testobject="to"),
    ]

    def test_cant_create_unknown_testcase(
        self, in_memory_notifier, dummy_backend, domain_config
    ):
        with pytest.raises(TestCaseUnknownError) as err:
            TestCaseFactory.create(
                ttype=TestType.UNKNOWN,
                testobject=self.testobject,
                specs=self.specifications,
                domain_config=domain_config,
                testrun_id=uuid4(),
                backend=dummy_backend,
                notifiers=[in_memory_notifier],
            )

        assert "not implemented!" in str(err)

    def test_creating_testcases(self, dummy_backend, in_memory_notifier, domain_config):
        testcase = TestCaseFactory.create(
            ttype=TestType.DUMMY_OK,
            testobject=self.testobject,
            specs=self.specifications,
            domain_config=domain_config,
            testrun_id=uuid4(),
            backend=dummy_backend,
            notifiers=[in_memory_notifier, in_memory_notifier],
        )

        assert testcase.ttype == TestType.DUMMY_OK
        assert testcase.status.value == "INITIATED"
        assert testcase.result.value == "N/A"
        for notifier in testcase.notifiers:
            assert isinstance(notifier, type(in_memory_notifier))
            assert "Initiating testcase" in notifier.notifications[0]
