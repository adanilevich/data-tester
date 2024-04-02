import os

from src.testcase.di.di import DependencyInjector
from src.testcase.driver_adapters.cli_testcase_runner import CliTestCaseRunner


testobjects = [
    {"domain": "my_domain", "project": "my_project", "instance": "my_instance",
     "name": "my_testobject_1"},
    {"domain": "my_domain", "project": "my_project", "instance": "my_instance",
     "name": "my_testobject_2"},
    {"domain": "my_domain", "project": "my_project", "instance": "my_instance",
     "name": "my_testobject_3"},
]

domain_config = {
    "domain": "my_domain",
    "compare_sample_default_sample_size": 1000,
    "compare_sample_sample_size_per_object": {"my_testobject_1": 100}
}

specs = [
    {"type": "schema", "content": "any", "location": "my_location", "valid": True},
    {"type": "sql", "content": "any", "location": "my_location", "valid": True},
]

testtypes = ["DUMMY_OK", "DUMMY_NOK", "DUMMY_EXCEPTION"]

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

    assert len(results) == 3

    testtype_to_result_mapper = {
        "DUMMY_OK": "OK", "DUMMY_NOK": "NOK", "DUMMY_EXCEPTION": "N/A"
    }

    for result in results:
        assert result["result"] == testtype_to_result_mapper[result["testtype"]]


