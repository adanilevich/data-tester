import os
from typing import List

from src.testcase.di.di import DependencyInjector
from src.testcase.drivers.cli_testcase_runner import CliTestCaseRunner


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


testcases = [
    {"testobject": testobject, "testtype": testtype, "specs": specs(testobject),
     "domain_config": domain_config, "run_id": "my_run_id"}
    for testobject, testtype in zip(testobjects, testtypes)
]


def test_dummy_cli_execution():
    os.environ["DATATESTER_ENV"] = "DUMMY"
    command_handler = DependencyInjector().run_testcases_command_handler()
    runner = CliTestCaseRunner(handler=command_handler)

    results = runner.run_testcases(testcases=testcases)

    # assume as many results are returned as testcases defined
    assert len(results) == len(testcases)

    # assume that results are mapped correctly
    testtype_to_result_mapper = {
        "DUMMY_OK": ("OK", "FINISHED"),
        "DUMMY_NOK": ("NOK", "FINISHED"),
        "DUMMY_EXCEPTION": ("N/A", "ERROR"),
        "UNKNOWN": ("N/A", "ERROR")
    }

    for result in results:
        testtype = result["testtype"]
        testcase_result = result["result"]
        testcase_status = result["status"]
        expected_result = testtype_to_result_mapper[testtype][0]
        expected_status = testtype_to_result_mapper[testtype][1]
        run_id = result["run_id"]
        assert testcase_result == expected_result
        assert testcase_status == expected_status
        assert run_id == "my_run_id"
