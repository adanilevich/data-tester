import os
from typing import List
from uuid import uuid4
from datetime import datetime

from src.apps.cli.testcase_di import TestCaseDependencyInjector
from src.config import Config
from src.dtos import (
    TestType,
    TestResult,
    TestStatus,
    TestObjectDTO,
    SpecificationDTO,
    SpecificationType,
    DomainConfigDTO,
    LocationDTO,
    TestCasesConfigDTO,
    SchemaTestCaseConfigDTO,
    CompareTestCaseConfigDTO,
    TestDefinitionDTO,
)
from src.dtos.testcase import TestRunDTO


testobjects = [
    {
        "domain": "my_domain",
        "stage": "my_stage",
        "instance": "my_instance",
        "name": "my_testobject_1",
    },
    {
        "domain": "my_domain",
        "stage": "my_stage",
        "instance": "my_instance",
        "name": "my_testobject_2",
    },
    {
        "domain": "my_domain",
        "stage": "my_stage",
        "instance": "my_instance",
        "name": "my_testobject_3",
    },
    {
        "domain": "my_domain",
        "stage": "my_stage",
        "instance": "my_instance",
        "name": "my_testobject_4",
    },
]

testtypes = ["DUMMY_OK", "DUMMY_NOK", "DUMMY_EXCEPTION", "UNKNOWN"]

domain_config = {
    "domain": "my_domain",
    "instances": {},
    "testreports_location": {"path": "dict://my_location"},
    "specifications_locations": [],
    "testcases": {
        "compare": {"sample_size": 100},
        "schema": {"compare_datatypes": ["int", "str"]},
    },
}


def specs(testobject: dict):
    specs: List[dict] = [
        {"spec_type": "schema", "location": "my_location", "columns": {"a": "int"}},
        {"spec_type": "rowcount_sql", "location": "my_location", "query": "SELECT"},
    ]

    [spec.update({"testobject": testobject["name"]}) for spec in specs]
    return specs


MY_UUID = uuid4()

# Refactor testcases to be a list of TestDefinitionDTO, not dicts
testcases = [
    TestDefinitionDTO(
        testobject=TestObjectDTO(**testobject),
        testtype=TestType(testtype),
        specs=[
            SpecificationDTO(
                spec_type=SpecificationType.SCHEMA,
                location=LocationDTO(path="dict://my_location"),
                testobject=testobject["name"],
            ),
            SpecificationDTO(
                spec_type=SpecificationType.ROWCOUNT_SQL,
                location=LocationDTO(path="dict://my_location"),
                testobject=testobject["name"],
            ),
        ],
        domain_config=DomainConfigDTO(
            domain="my_domain",
            instances={},
            specifications_locations=[],
            testreports_location=LocationDTO("dict://my_location"),
            testcases=TestCasesConfigDTO(
                schema=SchemaTestCaseConfigDTO(compare_datatypes=["int", "str"]),
                compare=CompareTestCaseConfigDTO(sample_size=100),
            ),
        ),
        testrun_id=MY_UUID,
    )
    for testobject, testtype in zip(testobjects, testtypes, strict=False)
]


def test_cli_execution_with_dummy_testcases():
    # Given: Set up environment for dummy platform
    os.environ["DATATESTER_ENV"] = "DUMMY"
    os.environ["DATATESTER_DATA_PLATFORM"] = "DUMMY"
    os.environ["DATATESTER_NOTIFIERS"] = '["IN_MEMORY", "STDOUT"]'

    # And: Create config and dependency injector
    config = Config()
    dependency_injector = TestCaseDependencyInjector(config)
    # The correct method is testrun_manager, not testcase_runner
    runner = dependency_injector.cli_testrun_manager()

    # When: Execute testrun with defined testcases
    testrun = TestRunDTO(
        testrun_id=MY_UUID,
        testset_id=uuid4(),
        labels=[],
        testset_name="testset",
        stage="my_stage",
        instance="my_instance",
        domain="my_domain",
        domain_config=testcases[0].domain_config,
        start_ts=datetime.now(),
        end_ts=None,
        status=TestStatus.INITIATED,
        result=TestResult.NA,
        testdefinitions=testcases,
        testcase_results=[],
    )
    result = runner.execute_testrun(testrun)

    # Then: Results should match expectations
    assert len(result.testcase_results) == len(testcases)
    testtype_to_result_mapper = {
        TestType.DUMMY_OK: (TestResult.OK, TestStatus.FINISHED),
        TestType.DUMMY_NOK: (TestResult.NOK, TestStatus.FINISHED),
        TestType.DUMMY_EXCEPTION: (TestResult.NA, TestStatus.ERROR),
        TestType.UNKNOWN: (TestResult.NA, TestStatus.ERROR),
    }
    for testcase_result in result.testcase_results:
        testtype = testcase_result.testtype
        expected_result, expected_status = testtype_to_result_mapper[testtype]
        assert testcase_result.result == expected_result
        assert testcase_result.status == expected_status
        assert testcase_result.testrun_id == MY_UUID
        # Additional field checks for coverage
        assert testcase_result.testobject is not None
        assert testcase_result.start_ts is not None
        assert testcase_result.end_ts is not None
        assert testcase_result.domain_config is not None
        assert isinstance(testcase_result.specifications, list)
        assert isinstance(testcase_result.labels, list)


def test_cli_execution_with_empty_testcases():
    # Given: Set up environment for dummy platform
    os.environ["DATATESTER_ENV"] = "DUMMY"
    os.environ["DATATESTER_DATA_PLATFORM"] = "DUMMY"
    os.environ["DATATESTER_NOTIFIERS"] = '["IN_MEMORY", "STDOUT"]'
    config = Config()
    dependency_injector = TestCaseDependencyInjector(config)
    runner = dependency_injector.cli_testrun_manager()
    # When: Execute testrun with no testcases
    testrun = TestRunDTO(
        testrun_id=uuid4(),
        testset_id=uuid4(),
        labels=[],
        testset_name="testset",
        stage="my_stage",
        instance="my_instance",
        domain="my_domain",
        domain_config=testcases[0].domain_config,
        start_ts=datetime.now(),
        end_ts=None,
        status=TestStatus.INITIATED,
        result=TestResult.NA,
        testdefinitions=[],
        testcase_results=[],
    )
    result = runner.execute_testrun(testrun)
    # Then: Should return a testrun with no results
    assert result.testcase_results == []


def test_cli_execution_with_invalid_testcase():
    # Given: Set up environment for dummy platform
    os.environ["DATATESTER_ENV"] = "DUMMY"
    os.environ["DATATESTER_DATA_PLATFORM"] = "DUMMY"
    os.environ["DATATESTER_NOTIFIERS"] = '["IN_MEMORY", "STDOUT"]'
    config = Config()
    dependency_injector = TestCaseDependencyInjector(config)
    runner = dependency_injector.cli_testrun_manager()
    # When: Execute testrun with an invalid testcase (unknown testtype)
    invalid_definition = TestDefinitionDTO(
        testobject=TestObjectDTO(**testobjects[0]),
        testtype=TestType.UNKNOWN,  # use enum, not string
        specs=[],
        domain_config=DomainConfigDTO(
            domain="my_domain",
            instances={},
            specifications_locations=[],
            testreports_location=LocationDTO("dict://my_location"),
            testcases=TestCasesConfigDTO(
                schema=SchemaTestCaseConfigDTO(compare_datatypes=["int", "str"]),
                compare=CompareTestCaseConfigDTO(sample_size=100),
            ),
        ),
        testrun_id=MY_UUID,
    )
    testrun = TestRunDTO(
        testrun_id=MY_UUID,
        testset_id=uuid4(),
        labels=[],
        testset_name="testset",
        stage="my_stage",
        instance="my_instance",
        domain="my_domain",
        domain_config=invalid_definition.domain_config,
        start_ts=datetime.now(),
        end_ts=None,
        status=TestStatus.INITIATED,
        result=TestResult.NA,
        testdefinitions=[invalid_definition],
        testcase_results=[],
    )
    result = runner.execute_testrun(testrun)
    # Then: Should return a testcase result with NA and ERROR status
    assert len(result.testcase_results) == 1
    testcase_result = result.testcase_results[0]
    assert testcase_result.result == TestResult.NA
    assert testcase_result.status == TestStatus.ERROR
    assert testcase_result.testrun_id == MY_UUID
    assert "unknown" in testcase_result.summary.lower()
