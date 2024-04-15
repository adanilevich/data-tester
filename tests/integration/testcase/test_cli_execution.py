import os

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
    "schema_testcase_config": {"compare_data_types": ["int", "str"]},
    "compare_sample_testcase_config": {
        "sample_size": 1000,
        "sample_size_per_object": {"my_testobject_1": 100}
    }
}

specs = [
    {"type": "schema", "location": "my_location"},
    {"type": "sql", "location": "my_location"},
]

testcases = [
    {"testobject": testobject, "testtype": testtype, "specs": specs,
     "domain_config": domain_config}
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
        assert testcase_result == expected_result
        assert testcase_status == expected_status