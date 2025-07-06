import pytest

from src.testcase.core.testcases import AbstractTestCase
from src.dtos import SchemaSpecificationDTO, TestType


class TestSchemaTestCase:

    spec = SchemaSpecificationDTO(
        location="this_location",
        columns={"a": "int", "b": "string", "c": "array"},
        partition_columns=["a"],
        clustering_columns=["b"],
        primary_keys=["a", "b"],
        testobject="stage_customers",
    )

    @pytest.fixture
    def testcase(self, testcase_creator) -> AbstractTestCase:

        testcase_ = testcase_creator.create(ttype=TestType.SCHEMA)

        # patch backend to return required resuls
        def get_schema_(*args, **kwargs) -> SchemaSpecificationDTO:
            return self.spec

        def harmonize_schema_(schema) -> SchemaSpecificationDTO:
            return schema

        testcase_.backend.get_schema = get_schema_
        testcase_.backend.harmonize_schema = harmonize_schema_
        testcase_.backend.supports_clustering = True
        testcase_.backend.supports_partitions = True
        testcase_.backend.supports_primary_keys = True
        testcase_.specs = [self.spec]

        return testcase_

    def test_that_result_is_ok_for_column_comparison(self, testcase):

        testcase._execute()

        assert testcase.result == testcase.result.OK
        assert {"Specification": "this_location"} in testcase.facts

    def test_that_result_is_nok_if_pk_comparison_fails(self, testcase):
        spec = SchemaSpecificationDTO(**self.spec.to_dict())
        spec.primary_keys = ["a"]  # this sould run in an error
        testcase.specs = [spec]

        testcase._execute()

        assert testcase.result == testcase.result.NOK
        assert "Schema deviates from specification" in testcase.summary
        assert "Primary key comparison: NOK" in testcase.summary
        assert {"Primary Keys Comparison": str({
            "expected_primary_keys": ["a"],
            "actual_primary_keys": ["a", "b"],
        })} in testcase.details

    def test_that_result_is_nok_if_column_comparison_fails(self, testcase):
        spec = SchemaSpecificationDTO(**self.spec.to_dict())
        spec.columns = {"a": "int", "b": "bool"}  # this sould run in an error
        testcase.specs = [spec]

        testcase._execute()

        assert testcase.result == testcase.result.NOK
        assert "Schema deviates from specification" in testcase.summary
        assert "Column comparison: NOK" in testcase.summary

        diff = testcase.diff["column_diff"]
        for entry in diff:
            if entry["expected_column"] == "a":
                assert entry["result_all"] == "OK"
                assert entry["result_column"] == "OK"
                assert entry["result_dtype"] == "OK"
            elif entry["expected_column"] == "b":
                assert entry["result_all"] == "NOK"
                assert entry["result_column"] == "OK"
                assert entry["result_dtype"] == "NOK"
            if entry["actual_column"] == "c":
                assert entry["expected_column"] is None
                assert entry["result_column"] == "NOK"
                assert entry["result_dtype"] is None
                assert entry["result_all"] == "NOK"

    def test_that_column_comparison_only_compares_configured_dtypes(self, testcase):
        # first the expected schema deviates from actual schema in column 'c'
        # in a datatype which is not relevant for comparison - here 'unknown'
        # this deviation should be ignored
        spec = SchemaSpecificationDTO(**self.spec.to_dict())
        spec.columns = {"a": "int", "b": "string", "c": "unknown"}
        testcase.specs = [spec]

        testcase._execute()

        assert testcase.result == testcase.result.OK

        # next, the specified datatype for column 'c' is a known one
        # since it deviates from actual schema, the test fails
        spec = SchemaSpecificationDTO(**self.spec.to_dict())
        spec.columns = {"a": "int", "b": "string", "c": "int"}  # this should fail
        testcase.specs = [spec]

        testcase._execute()

        assert testcase.result == testcase.result.NOK

    def test_if_backend_only_supports_column_comparison(self, testcase):
        testcase.backend.supports_partitions = False
        testcase.backend.supports_clustering = False
        testcase.backend.supports_primary_keys = False

        testcase._execute()

        assert testcase.result == testcase.result.OK
        summary = "Schema corresponds to specification: Column comparison: OK;"
        assert testcase.summary == summary
