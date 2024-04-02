import pytest

from src.testcase.dtos import TestObjectDTO, SpecificationDTO, DomainConfigDTO
from src.testcase.testcases.testcase_factory import TestCaseFactory, TestCaseUnknownError


class TestTestCaseFactory:

    testobject = TestObjectDTO(name="to", domain="dom", project="proj", instance="inst")
    specifications = [
        SpecificationDTO(type="schema", content=None, location="loc", valid=True),
        SpecificationDTO(type="sql", content="sdfs", location="loc", valid=False),
    ]
    domain_config = DomainConfigDTO(
        domain="my_domain",
        compare_sample_default_sample_size=2,
        compare_sample_sample_size_per_object=dict()
    )

    def test_cant_create_unknown_testcase(self, in_memory_notifier, dummy_backend):

        with pytest.raises(TestCaseUnknownError) as err:
            TestCaseFactory.create(
                ttype="unknown",
                testobject=self.testobject,
                specs=self.specifications,
                domain_config=self.domain_config,
                run_id="my_run_id",
                backend=dummy_backend,
                notifiers=[in_memory_notifier]
            )

        assert "Testcase unknown is not implemented!" in str(err)

    def test_creating_testcases(self, dummy_backend, in_memory_notifier):
        testcase = TestCaseFactory.create(
            ttype="DUMMY_OK",
            testobject=self.testobject,
            specs=self.specifications,
            domain_config=self.domain_config,
            run_id="my_run_id",
            backend=dummy_backend,
            notifiers=[in_memory_notifier, in_memory_notifier]
        )

        assert testcase.ttype == "DUMMY_OK"
        assert testcase.status.value == "INITIATED"
        assert testcase.result.value == "N/A"
        for notifier in testcase.notifiers:
            assert isinstance(notifier, type(in_memory_notifier))
            assert "Initiating testcase" in notifier.notifications[0]
