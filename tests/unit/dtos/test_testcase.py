import pytest
from datetime import datetime
from uuid import uuid4

from src.dtos.testrun_dtos import (
    TestRunDefDTO,
    TestRunDTO,
    TestCaseDefDTO,
    Status,
    Result,
    TestType,
)
from src.dtos.testset_dtos import TestSetDTO, TestCaseEntryDTO
from src.dtos.specification_dtos import (
    AnySpec,
    CompareSpecDTO,
    RowcountSpecDTO,
    SchemaSpecDTO,
)
from src.dtos.domain_config_dtos import (
    DomainConfigDTO,
    TestCasesConfigDTO,
    CompareTestCaseConfigDTO,
    SchemaTestCaseConfigDTO,
)
from src.dtos.storage_dtos import LocationDTO


@pytest.fixture
def domain_config():
    """Create a valid DomainConfigDTO for testing."""
    return DomainConfigDTO(
        domain="test_domain",
        instances={"dev": ["instance1"], "prod": ["instance2"]},
        specifications_locations=LocationDTO(path="dummy://specs"),
        testreports_location=LocationDTO(path="dummy://reports"),
        testcases=TestCasesConfigDTO(
            compare=CompareTestCaseConfigDTO(sample_size=100),
            schema=SchemaTestCaseConfigDTO(compare_datatypes=["string", "int"]),
        ),
    )


class TestTestRunDefDTO:
    def test_from_testset_creates_testrun_def_correctly(self, domain_config):
        testset = TestSetDTO(
            testset_id=uuid4(),
            name="Test Set 1",
            description="A test set",
            labels=["label1", "label2"],
            domain="test_domain",
            default_stage="dev",
            stage="uat",
            default_instance="instance1",
            instance="main",
            testcases={
                "table1_SCHEMA": TestCaseEntryDTO(
                    testobject="table1",
                    testtype=TestType.SCHEMA,
                    domain="test_domain",
                    comment="Schema test",
                ),
                "table2_ROWCOUNT": TestCaseEntryDTO(
                    testobject="table2",
                    testtype=TestType.ROWCOUNT,
                    domain="test_domain",
                    comment="Row count test",
                ),
            },
        )

        spec_list: list[list[AnySpec]] = [
            [
                SchemaSpecDTO(
                    location=LocationDTO(path="dummy://spec1"), testobject="table1"
                )
            ],
            [
                RowcountSpecDTO(
                    location=LocationDTO(path="dummy://spec2"), testobject="table2"
                )
            ],
        ]

        testrun_def = TestRunDefDTO.from_testset(testset, spec_list, domain_config)

        assert testrun_def.testset_id == testset.testset_id
        assert testrun_def.testset_name == "Test Set 1"
        assert testrun_def.labels == ["label1", "label2"]
        assert testrun_def.domain == "test_domain"
        assert testrun_def.stage == "uat"
        assert testrun_def.instance == "main"
        assert testrun_def.domain_config == domain_config
        assert len(testrun_def.testcase_defs) == 2

    def test_from_testset_validates_spec_list_length(self, domain_config):
        testset = TestSetDTO(
            name="Test Set",
            domain="test_domain",
            default_stage="dev",
            default_instance="instance1",
            testcases={
                "table1_SCHEMA": TestCaseEntryDTO(
                    testobject="table1", domain="test_domain", testtype=TestType.SCHEMA
                ),
                "table2_ROWCOUNT": TestCaseEntryDTO(
                    testobject="table2", testtype=TestType.ROWCOUNT, domain="test_domain"
                ),
            },
        )

        spec_list: list[list[AnySpec]] = [
            [
                SchemaSpecDTO(
                    location=LocationDTO(path="dummy://spec1"), testobject="table1"
                )
            ]
        ]

        msg = "spec_list must be same length as testset.testcases"
        with pytest.raises(ValueError, match=msg):
            TestRunDefDTO.from_testset(testset, spec_list, domain_config)

    def test_from_testset_validates_domain_config_matches_testset(self):
        testset = TestSetDTO(
            name="Test Set",
            domain="test_domain",
            default_stage="dev",
            default_instance="instance1",
            testcases={
                "table1_SCHEMA": TestCaseEntryDTO(
                    testobject="table1", testtype=TestType.SCHEMA, domain="test_domain"
                )
            },
        )

        spec_list: list[list[AnySpec]] = [
            [
                SchemaSpecDTO(
                    location=LocationDTO(path="dummy://spec1"), testobject="table1"
                )
            ]
        ]

        different_domain_config = DomainConfigDTO(
            domain="different_domain",
            instances={"dev": ["instance1"]},
            specifications_locations=LocationDTO(path="dummy://specs"),
            testreports_location=LocationDTO(path="dummy://reports"),
            testcases=TestCasesConfigDTO(
                compare=CompareTestCaseConfigDTO(sample_size=100),
                schema=SchemaTestCaseConfigDTO(compare_datatypes=["string"]),
            ),
        )

        msg = "domain_config.domain must be same as testset.domain"
        with pytest.raises(ValueError, match=msg):
            TestRunDefDTO.from_testset(testset, spec_list, different_domain_config)

    def test_from_testset_creates_proper_testcase_defs(self, domain_config):
        testset = TestSetDTO(
            testset_id=uuid4(),
            name="Test Set",
            domain="test_domain",
            default_stage="dev",
            default_instance="instance1",
            labels=["integration", "daily"],
            testcases={
                "table1_COMPARE_yesterday": TestCaseEntryDTO(
                    testobject="table1",
                    testtype=TestType.COMPARE,
                    domain="test_domain",
                    scenario="yesterday",
                )
            },
        )

        spec_list: list[list[AnySpec]] = [
            [
                CompareSpecDTO(
                    location=LocationDTO(path="dummy://spec1"), testobject="table1"
                ),
                CompareSpecDTO(
                    location=LocationDTO(path="dummy://spec2"), testobject="table1"
                ),
            ]
        ]

        testrun_def = TestRunDefDTO.from_testset(testset, spec_list, domain_config)

        assert len(testrun_def.testcase_defs) == 1
        tc_def = testrun_def.testcase_defs[0]

        assert tc_def.testobject.name == "table1"
        assert tc_def.testobject.domain == "test_domain"
        assert tc_def.testobject.stage == "dev"
        assert tc_def.testobject.instance == "instance1"
        assert tc_def.testtype == TestType.COMPARE
        assert tc_def.scenario == "yesterday"
        assert len(tc_def.specs) == 2
        assert tc_def.labels == ["integration", "daily"]
        assert tc_def.testset_id == testset.testset_id
        assert tc_def.testset_name == "Test Set"
        assert tc_def.domain_config == domain_config

    def test_testcase_def_has_no_testrun_id(self, domain_config):
        """TestCaseDefDTO must not carry a testrun_id."""
        assert not hasattr(TestCaseDefDTO.model_fields, "testrun_id")


class TestTestRunDTOAutoSummary:
    def test_summary_computed_on_creation(self, domain_config):
        from src.dtos.testrun_dtos import TestCaseDTO, TestObjectDTO

        testobject = TestObjectDTO(
            name="t", domain="test_domain", stage="dev", instance="instance1"
        )
        tc = TestCaseDTO(
            id=uuid4(),
            testrun_id=uuid4(),
            testobject=testobject,
            testtype=TestType.SCHEMA,
            status=Status.FINISHED,
            result=Result.OK,
            diff={},
            summary="ok",
            facts=[],
            details=[],
            specs=[],
            domain_config=domain_config,
            start_ts=datetime.now(),
            end_ts=datetime.now(),
            labels=[],
            domain="test_domain",
            stage="dev",
            instance="instance1",
        )

        testrun = TestRunDTO(
            id=uuid4(),
            testset_id=uuid4(),
            domain="test_domain",
            stage="dev",
            instance="instance1",
            result=Result.OK,
            status=Status.FINISHED,
            start_ts=datetime.now(),
            results=[tc],
            testdefinitions=[],
            domain_config=domain_config,
        )

        assert testrun.summary.completed_testcases == 1
        assert testrun.summary.ok_testcases == 1
        assert testrun.summary.nok_testcases == 0

    def test_id_is_a_field_not_property(self, domain_config):
        testrun_id = uuid4()
        testrun = TestRunDTO(
            id=testrun_id,
            testset_id=uuid4(),
            domain="test_domain",
            stage="dev",
            instance="instance1",
            result=Result.OK,
            status=Status.FINISHED,
            start_ts=datetime.now(),
            testdefinitions=[],
            domain_config=domain_config,
        )

        assert testrun.id == testrun_id
        # id is a plain field (UUID4), not a string property
        import uuid
        assert isinstance(testrun.id, uuid.UUID)
