import pytest
import polars as pl

from src.testcase.testcases import AbstractTestCase
from src.dtos import RowCountSqlDTO


# noinspection PyUnusedLocal
class TestRowCountTestCase:
    spec = RowCountSqlDTO(
        location="this_location",
        query="to be replaced by test",
        testobject="stage_customers",
    )

    @pytest.fixture
    def testcase(self, testcase_creator) -> AbstractTestCase:

        testcase_ = testcase_creator.create(ttype="ROWCOUNT")

        def run_query_(query, *args, **kwargs) -> pl.DataFrame:
            if "good" in query:
                return pl.DataFrame(
                    {"count": [10, 10], "__source__": ["expected", "actual"]}
                )
            elif "strange" in query:  # backend should never return more than 2 counts
                return pl.DataFrame(
                    {"count": [10, 5, 3], "__source__": ["expected", "actual", "df"]}
                )
            elif "bad" in query:
                return pl.DataFrame(
                    {"count": [10, 5], "__source__": ["expected", "actual"]}
                )
            elif "exception" in query:
                raise ValueError("This is a simulated exception.")
            else:
                return pl.DataFrame()

        testcase_.backend.run_query = run_query_
        testcase_.specs = [self.spec]

        return testcase_

    def test_execution_stops_if_invalid_query_is_provided(self, testcase):
        self.spec.query = "strange"
        testcase.specs = [self.spec]

        testcase._execute()

        assert testcase.status == testcase.status.ABORTED
        assert testcase.result == testcase.result.NA
        assert "Rowcount validation failed" in testcase.summary

    def test_result_is_nok_if_counts_deviate(self, testcase):
        self.spec.query = "bad"
        testcase.specs = [self.spec]

        testcase._execute()

        assert testcase.result == testcase.result.NOK
        assert testcase.summary == ("Actual rowcount (5) deviates from expected "
                                    "rowcount (10)!")
        assert "rowcount_diff" in testcase.diff

    def test_that_backend_exception_is_caught(self, testcase):
        self.spec.query = "exception"
        testcase.specs = [self.spec]

        with pytest.raises(ValueError) as err:
            testcase._execute()

        assert testcase.result == testcase.result.NA
        assert "simulated exception" in str(err)

    def test_happy_path(self, testcase):
        self.spec.query = "good"
        testcase.specs = [self.spec]

        testcase._execute()

        assert testcase.result == testcase.result.OK
        assert testcase.summary == "Actual rowcount (10) matches expected rowcount."
        assert "rowcount_diff" in testcase.diff
