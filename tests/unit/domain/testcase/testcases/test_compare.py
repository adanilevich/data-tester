from typing import List

import pytest
import time
import polars as pl

from src.domain.testcase.core.testcases import CompareTestCase
from src.dtos import (
    SchemaSpecificationDTO,
    CompareSqlDTO,
    TestType,
    SpecificationType,
    LocationDTO,
)


# noinspection PyUnusedLocal
class TestCompareTestCase:
    schema = SchemaSpecificationDTO(
        location=LocationDTO(path="dummy://this_location"),
        columns={"a": "int", "b": "string", "c": "bool"},
        primary_keys=["a", "b"],
        testobject="stage_customers",
        spec_type=SpecificationType.COMPARE_SQL,
    )

    sql = CompareSqlDTO(
        location=LocationDTO(path="dummy://this_location"),
        query="this_will_be_changed",
        testobject="stage_customers",
        spec_type=SpecificationType.COMPARE_SQL,
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

        def get_schema_from_query(*args, **kwargs) -> SchemaSpecificationDTO:
            return self.schema

        testcase_.backend.get_schema_from_query = get_schema_from_query

        def get_sample_keys_(query, *args, **kwargs) -> List[str]:
            if "exception" in query:
                raise NotImplementedError("This is a simulated exception.")
            else:
                return self.data.select("__concat_key__").to_series().to_list()

        testcase_.backend.get_sample_keys = get_sample_keys_

        def get_sample_from_query_(query, *args, **kwargs) -> pl.DataFrame:
            if "error" in query:
                raise NotImplementedError("This is a simulated exception.")
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
        testcase.domain_config.testcases.compare.sample_size_per_object = {}
        testcase.domain_config.testcases.compare.sample_size = 1

        assert testcase.sample_size == 1

    def test_specific_sample_size_is_used_if_specified(self, testcase):
        sizes = {testcase.testobject.name: 100}
        testcase.domain_config.testcases.compare.sample_size_per_object = sizes
        testcase.domain_config.testcases.compare.sample_size = 1

        assert testcase.sample_size == 100

    def test_key_sampling_exception_is_caught(self, testcase):
        sql = CompareSqlDTO.from_dict(self.sql.to_dict())
        sql.query = "exception"
        testcase.specs = [sql, self.schema]

        with pytest.raises(NotImplementedError) as err:
            testcase._execute()

        assert "Error while sampling primary keys" in str(err)
        assert "simulated exception" in str(err)

    def test_happy_path(self, testcase):
        testcase._execute()

        assert testcase.result == testcase.result.OK
        assert "from testobject equals sample from test sql" in testcase.summary

    def test_that_diff_is_treated_correctly(self, testcase):
        sql = CompareSqlDTO.from_dict(self.sql.to_dict())
        sql.query = "bad"
        testcase.specs = [sql, self.schema]

        testcase._execute()

        assert testcase.result == testcase.result.NOK
        assert "compare_diff" in testcase.diff
        assert testcase.summary == "Testobject differs from SQL in 1 row(s)."

    # skip performance test, only execute if needed
    @pytest.mark.skipif(True, reason="Only run performance test on demand")
    def test_in_memory_comparison_performance(self, testcase, performance_test_data):
        """
        Test speed of diff comparison. Result expectations so far:
            - dataset of ca 12 Mio rows, 150 columns, compared with itself (one version
                truncated and casted to string:
                - fixtures download and preparation: ca 45 s
                - comparison duration if no casting required: 9 s (almost all for rowhash)
                - comparison if dynamic casting required: 380 s (50/50 casting/rowhash)
                - comparison duration if to-string casting: 330 s (50/50 casting/rowhash)
                - comparison duration if only one col is casted: ca 70 s
        """

        print("\nStarting performance tests for compare ...")

        def compare_data(df, other_df):
            print("Comparing dataframes of shapes", df.shape, other_df.shape)
            start_ = time.time()
            diff_ = testcase._compare(df, other_df)
            end_ = time.time()
            comparison_time = end_ - start_
            print("\nData comparison time: ", comparison_time, "s")
            return diff_

        # truncate to provoke difference and cast first column to string to force
        # testcase._get_diff to cast dataframes
        this = performance_test_data.with_columns(pl.lit("value").alias("__concat_key__"))
        that = (
            this[:-10]
            # .cast({this.columns[0]: pl.String})
            # .reverse()
        )

        diff = compare_data(this, that)
        assert diff.shape[0] == 10
