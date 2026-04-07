import polars as pl
import pytest
from src.domain.testrun.testcases import AbstractTestCase
from src.domain.testrun.testcases.rowcount import RowCountTestCaseError
from src.dtos import LocationDTO, RowcountSpecDTO, SpecType, TestType


# noinspection PyUnusedLocal
class TestRowCountTestCase:
    @pytest.fixture
    def spec(self) -> RowcountSpecDTO:
        return RowcountSpecDTO(
            location=LocationDTO(path="dummy://this_location"),
            query="to be replaced by test",
            testobject="stage_customers",
            spec_type=SpecType.ROWCOUNT,
        )

    @pytest.fixture
    def testcase(self, testcase_creator, spec) -> AbstractTestCase:
        testcase_ = testcase_creator.create(ttype=TestType.ROWCOUNT)

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
        testcase_.specs = [spec]

        return testcase_

    def test_execution_stops_if_invalid_query_is_provided(self, testcase, spec):
        spec.query = "strange"
        testcase.specs = [spec]

        testcase._execute()

        assert testcase.status == testcase.status.ABORTED
        assert testcase.result == testcase.result.NA
        assert "Rowcount validation failed" in testcase.summary

    def test_result_is_nok_if_counts_deviate(self, testcase, spec):
        spec.query = "bad"
        testcase.specs = [spec]

        testcase._execute()

        assert testcase.result == testcase.result.NOK
        assert testcase.summary == (
            "Actual rowcount (5) deviates from expected rowcount (10)!"
        )
        assert "rowcount_diff" in testcase.diff

    def test_that_backend_exception_is_caught(self, testcase, spec):
        spec.query = "exception"
        testcase.specs = [spec]

        with pytest.raises(RowCountTestCaseError):
            testcase._execute()

        assert testcase.result == testcase.result.NA

    def test_happy_path(self, testcase, spec):
        spec.query = "good"
        testcase.specs = [spec]

        testcase._execute()

        assert testcase.result == testcase.result.OK
        assert testcase.summary == "Actual rowcount (10) matches expected rowcount."
        assert "rowcount_diff" in testcase.diff
