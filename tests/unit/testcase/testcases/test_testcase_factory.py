import pytest

from src.dtos.testcase import TestObjectDTO
from src.dtos.configs import (
    SchemaTestCaseConfigDTO, CompareSampleTestCaseConfigDTO, DomainConfigDTO
)
from src.dtos.specifications import SpecificationDTO
from src.testcase.testcases import TestCaseFactory, TestCaseUnknownError


class TestTestCaseFactory:

    testobject = TestObjectDTO(name="to", domain="dom", project="proj", instance="inst")
    specifications = [
        SpecificationDTO(type="schema", location="loc"),
        SpecificationDTO(type="sql", location="loc"),
    ]
    domain_config = DomainConfigDTO(
        domain="my_domain",
        schema_testcase_config=SchemaTestCaseConfigDTO(compare_datatypes=["int", "str"]),
        compare_sample_testcase_config=CompareSampleTestCaseConfigDTO(sample_size=100)
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
