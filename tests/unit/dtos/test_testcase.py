import pytest
from datetime import datetime
from uuid import uuid4

from src.dtos.testcase import (
    TestRunDTO,
    TestStatus,
    TestResult,
    TestType,
)
from src.dtos.testset import TestSetDTO, TestCaseEntryDTO
from src.dtos.specification import SpecificationDTO, SpecificationType
from src.dtos.domain_config import (
    DomainConfigDTO,
    TestCasesConfigDTO,
    CompareTestCaseConfigDTO,
    SchemaTestCaseConfigDTO,
)
from src.dtos.storage import LocationDTO


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
            schema=SchemaTestCaseConfigDTO(compare_datatypes=["string", "int"])
        )
    )


class TestTestRunDTO:
    def test_from_testset_creates_testrun_correctly(self, domain_config):
        # Given a TestSetDTO with test cases
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
                    comment="Schema test"
                ),
                "table2_ROWCOUNT": TestCaseEntryDTO(
                    testobject="table2",
                    testtype=TestType.ROWCOUNT,
                    comment="Row count test"
                )
            }
        )

        # And specifications for each test case
        spec_list = [
            [SpecificationDTO(
                location=LocationDTO(path="dummy://spec1"),
                spec_type=SpecificationType.SCHEMA,
                testobject="table1"
            )],
            [SpecificationDTO(
                location=LocationDTO(path="dummy://spec2"),
                spec_type=SpecificationType.ROWCOUNT_SQL,
                testobject="table2"
            )]
        ]

        # When creating a TestRunDTO from the testset
        testrun = TestRunDTO.from_testset(testset, spec_list, domain_config)

        # Then the testrun should have correct attributes
        assert testrun.testset_id == testset.testset_id
        assert testrun.testset_name == "Test Set 1"
        assert testrun.labels == ["label1", "label2"]
        assert testrun.domain == "test_domain"
        assert testrun.stage == "uat"
        assert testrun.instance == "main"
        assert testrun.status == TestStatus.NOT_STARTED
        assert testrun.result == TestResult.NA
        assert testrun.end_ts is None
        assert isinstance(testrun.start_ts, datetime)
        assert len(testrun.testdefinitions) == 2
        assert len(testrun.testcase_results) == 0
        assert testrun.domain_config == domain_config

    def test_from_testset_validates_spec_list_length(self, domain_config):
        # Given a TestSetDTO with 2 test cases
        testset = TestSetDTO(
            name="Test Set",
            domain="test_domain",
            default_stage="dev",
            default_instance="instance1",
            testcases={
                "table1_SCHEMA": TestCaseEntryDTO(
                    testobject="table1",
                    testtype=TestType.SCHEMA
                ),
                "table2_ROWCOUNT": TestCaseEntryDTO(
                    testobject="table2",
                    testtype=TestType.ROWCOUNT
                )
            }
        )

        # And a spec_list with only 1 entry (mismatched length)
        spec_list = [[SpecificationDTO(
            location=LocationDTO(path="dummy://spec1"),
            spec_type=SpecificationType.SCHEMA,
            testobject="table1"
        )]]

        # When creating a TestRunDTO, it should raise ValueError
        msg = "spec_list must be same length as testset.testcases"
        with pytest.raises(ValueError, match=msg):
            TestRunDTO.from_testset(testset, spec_list, domain_config)

    def test_from_testset_validates_domain_config_matches_testset(self):
        # Given a TestSetDTO with domain "test_domain"
        testset = TestSetDTO(
            name="Test Set",
            domain="test_domain",
            default_stage="dev",
            default_instance="instance1",
            testcases={
                "table1_SCHEMA": TestCaseEntryDTO(
                    testobject="table1",
                    testtype=TestType.SCHEMA
                )
            }
        )

        spec_list = [[SpecificationDTO(
            location=LocationDTO(path="dummy://spec1"),
            spec_type=SpecificationType.SCHEMA,
            testobject="table1"
        )]]

        # And a domain config with different domain
        different_domain_config = DomainConfigDTO(
            domain="different_domain",
            instances={"dev": ["instance1"]},
            specifications_locations=LocationDTO(path="dummy://specs"),
            testreports_location=LocationDTO(path="dummy://reports"),
            testcases=TestCasesConfigDTO(
                compare=CompareTestCaseConfigDTO(sample_size=100),
                schema=SchemaTestCaseConfigDTO(compare_datatypes=["string"])
            )
        )

        # When creating a TestRunDTO, it should raise ValueError
        msg = "domain_config.domain must be same as testset.domain"
        with pytest.raises(ValueError, match=msg):
            TestRunDTO.from_testset(testset, spec_list, different_domain_config)

    def test_from_testset_creates_proper_test_definitions(self, domain_config):
        # Given a TestSetDTO with test case that has scenario
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
                    scenario="yesterday"
                )
            }
        )

        spec_list = [[
            SpecificationDTO(
                location=LocationDTO(path="dummy://spec1"),
                spec_type=SpecificationType.COMPARE_SQL,
                testobject="table1"
            ),
            SpecificationDTO(
                location=LocationDTO(path="dummy://spec2"),
                spec_type=SpecificationType.COMPARE_SQL,
                testobject="table1"
            )
        ]]

        # When creating a TestRunDTO
        testrun = TestRunDTO.from_testset(testset, spec_list, domain_config)

        # Then test definitions should be created correctly
        assert len(testrun.testdefinitions) == 1
        test_def = testrun.testdefinitions[0]

        assert test_def.testobject.name == "table1"
        assert test_def.testobject.domain == "test_domain"
        assert test_def.testobject.stage == "dev"
        assert test_def.testobject.instance == "instance1"
        assert test_def.testtype == TestType.COMPARE
        assert test_def.scenario == "yesterday"
        assert len(test_def.specs) == 2
        assert test_def.labels == ["integration", "daily"]
        assert test_def.testset_id == testset.testset_id
        assert test_def.testrun_id == testrun.testrun_id
        assert test_def.domain_config == domain_config

    def test_object_id_property(self, domain_config):
        # Given a TestRunDTO
        testrun_id = uuid4()
        testrun = TestRunDTO(
            testrun_id=testrun_id,
            testset_id=uuid4(),
            domain="test_domain",
            stage="dev",
            instance="instance1",
            result=TestResult.OK,
            status=TestStatus.FINISHED,
            start_ts=datetime.now(),
            testdefinitions=[],
            domain_config=domain_config
        )

        # Then object_id should return string representation of testrun_id
        assert testrun.object_id == str(testrun_id)
