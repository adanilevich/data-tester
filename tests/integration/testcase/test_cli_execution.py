import os
from typing import List
from uuid import uuid4

from src.testcase.di.di import DependencyInjector
from src.testcase.drivers.cli_testcase_runner import CliTestCaseRunner
from src.dtos import TestType, TestResult, TestStatus


testobjects = [
    {"domain": "my_domain", "stage": "my_stage", "instance": "my_instance",
     "name": "my_testobject_1"},
    {"domain": "my_domain", "stage": "my_stage", "instance": "my_instance",
     "name": "my_testobject_2"},
    {"domain": "my_domain", "stage": "my_stage", "instance": "my_instance",
     "name": "my_testobject_3"},
    {"domain": "my_domain", "stage": "my_stage", "instance": "my_instance",
     "name": "my_testobject_4"},
]

testtypes = ["DUMMY_OK", "DUMMY_NOK", "DUMMY_EXCEPTION", "UNKNOWN"]

domain_config = {
    "domain": "my_domain",
    "instances": {},
    "testreports_locations": [],
    "specifications_locations": [],
    "testmatrices_locations": "my_location",
    "testcases": {
        "compare_sample": {"sample_size": 100},
        "schema": {"compare_datatypes": ["int", "str"]}
    }
}


def specs(testobject: dict):
    specs: List[dict] = [
        {"type": "schema", "location": "my_location", "columns": {"a": "int"}},
        {"type": "rowcount_sql", "location": "my_location", "query": "SELECT"},
    ]

    [spec.update({"testobject": testobject["name"]}) for spec in specs]
    return specs

MY_UUID = uuid4()

testcases = [
    {"testobject": testobject, "testtype": testtype, "specs": specs(testobject),
     "domain_config": domain_config, "testrun_id": MY_UUID}
    for testobject, testtype in zip(testobjects, testtypes)
]


def test_cli_execution_with_dummy_testcases():
    os.environ["DATATESTER_ENV"] = "DUMMY"
    command_handler = DependencyInjector().run_testcases_command_handler()
    runner = CliTestCaseRunner(handler=command_handler)

    results = runner.run_testcases(testcases=testcases)

    # assume as many results are returned as testcases defined
    assert len(results) == len(testcases)

    # assume that results are mapped correctly
    testtype_to_result_mapper = {
        TestType.DUMMY_OK: (TestResult.OK, TestStatus.FINISHED),
        TestType.DUMMY_NOK: (TestResult.NOK, TestStatus.FINISHED),
        TestType.DUMMY_EXCEPTION: (TestResult.NA, TestStatus.ERROR),
        TestType.UNKNOWN: (TestResult.NA, TestStatus.ERROR)
    }

    for result in results:
        testtype = result["testtype"]
        testcase_result = result["result"]
        testcase_status = result["status"]
        expected_result = testtype_to_result_mapper[testtype][0]
        expected_status = testtype_to_result_mapper[testtype][1]
        testrun_id = result["testrun_id"]
        assert testcase_result == expected_result
        assert testcase_status == expected_status
        assert testrun_id == MY_UUID
