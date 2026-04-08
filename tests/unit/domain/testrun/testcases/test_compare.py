from typing import List

import polars as pl
import pytest
from src.domain.testrun.testcases.compare import (
    CompareTestCase,
    CompareTestCaseError,
    PrimaryKeysMissingError,
    QueryExecutionError,
    SchemaMismatchError,
)
from src.dtos import (
    CompareSpecDTO,
    LocationDTO,
    SchemaSpecDTO,
    SpecType,
    TestType,
)


# noinspection PyUnusedLocal
class TestCompareTestCase:
    schema = SchemaSpecDTO(
        location=LocationDTO(path="dummy://this_location"),
        columns={"a": "int", "b": "string", "c": "bool"},
        primary_keys=["a", "b"],
        testobject="stage_customers",
    )

    sql = CompareSpecDTO(
        location=LocationDTO(path="dummy://this_location"),
        query="this_will_be_changed",
        testobject="stage_customers",
        spec_type=SpecType.COMPARE,
    )

    data = pl.DataFrame(
        {
            "a": [1, 2, 3],
            "b": ["this", "that", "other"],
            "c": [True, False, True],
            "__concat_key__": ["1|this", "2|that", "3|other"],
        }
    )

    @pytest.fixture
    def testcase(self, testcase_creator) -> CompareTestCase:
        testcase_ = testcase_creator.create(ttype=TestType.COMPARE)

        def get_schema_from_query(*args, **kwargs) -> SchemaSpecDTO:
            return self.schema

        testcase_.backend.get_schema_from_query = get_schema_from_query

        def get_sample_keys_(query, *args, **kwargs) -> List[str]:
            if "exception" in query:
                raise CompareTestCaseError("This is a simulated exception.")
            else:
                return self.data.select("__concat_key__").to_series().to_list()

        testcase_.backend.get_sample_keys = get_sample_keys_

        def get_sample_from_query_(query, *args, **kwargs) -> pl.DataFrame:
            if "error" in query:
                raise CompareTestCaseError("This is a simulated exception.")
            if "bad" in query:
                return self.data[:-1]
            else:
                return self.data

        testcase_.backend.get_sample_from_query = get_sample_from_query_

        def get_sample_from_testobject_(*args, **kwargs) -> pl.DataFrame:
            return self.data

        testcase_.backend.get_sample_from_testobject = get_sample_from_testobject_

        testcase_.specs = [self.schema, self.sql]

        # noinspection PyTypeChecker
        return testcase_

    def test_default_sample_size_is_used_if_specific_not_specified(self, testcase):
        testcase.domain_config.sample_size_per_object = {}
        testcase.domain_config.sample_size_default = 1

        assert testcase.sample_size == 1

    def test_specific_sample_size_is_used_if_specified(self, testcase):
        sizes = {testcase.testobject.name: 100}
        testcase.domain_config.sample_size_per_object = sizes
        testcase.domain_config.sample_size_default = 1

        assert testcase.sample_size == 100

    def test_key_sampling_exception_is_caught(self, testcase):
        sql = self.sql.model_copy(update={"query": "exception"})
        testcase.specs = [sql, self.schema]

        with pytest.raises(CompareTestCaseError) as err:
            testcase._execute()

        assert "Error while sampling primary keys" in str(err)

    def test_happy_path(self, testcase):
        testcase._execute()

        assert testcase.result == testcase.result.OK
        assert "from testobject equals sample from test sql" in testcase.summary

    def test_that_diff_is_treated_correctly(self, testcase):
        sql = self.sql.model_copy(update={"query": "bad"})
        testcase.specs = [sql, self.schema]

        testcase._execute()

        assert testcase.result == testcase.result.NOK
        assert "compare_diff" in testcase.diff
        assert testcase.summary == "Testobject differs from SQL in 1 row(s)."

    def test_get_schema_from_query_failure(self, testcase):
        def raise_error(*args, **kwargs):
            raise RuntimeError("backend timeout")

        testcase.backend.get_schema_from_query = raise_error

        with pytest.raises(QueryExecutionError) as err:
            testcase._execute()

        assert "Error while obtaining schema from test query" in str(err)

    def test_primary_keys_missing_in_query(self, testcase):
        schema_without_pks = SchemaSpecDTO(
            location=LocationDTO(path="dummy://loc"),
            columns={"x": "int", "y": "string"},
            primary_keys=[],
            testobject="stage_customers",
        )

        def get_schema_without_pks(*args, **kwargs):
            return schema_without_pks

        testcase.backend.get_schema_from_query = get_schema_without_pks

        with pytest.raises(PrimaryKeysMissingError) as err:
            testcase._execute()

        assert "Primary keys are missing in query" in str(err)

    def test_sample_from_query_failure(self, testcase):
        sql = self.sql.model_copy(update={"query": "error"})
        testcase.specs = [sql, self.schema]

        with pytest.raises(QueryExecutionError) as err:
            testcase._execute()

        assert "Error while sampling from test query" in str(err)

    def test_sample_from_testobject_failure(self, testcase):
        def raise_error(*args, **kwargs):
            raise RuntimeError("testobject read failed")

        testcase.backend.get_sample_from_testobject = raise_error

        with pytest.raises(QueryExecutionError) as err:
            testcase._execute()

        assert "Error while sampling from testobject" in str(err)

    def test_schema_mismatch_raises_error(self, testcase):
        extra_col_data = self.data.with_columns(
            pl.lit("extra").alias("missing_col"),
        )

        def get_sample_with_extra(*args, **kwargs):
            return extra_col_data

        testcase.backend.get_sample_from_query = get_sample_with_extra

        with pytest.raises(SchemaMismatchError):
            testcase._execute()
