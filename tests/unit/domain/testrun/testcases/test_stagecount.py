import pytest
import polars as pl

from src.domain.testrun.testcases import AbstractTestCase
from src.domain.testrun.testcases.stagecount import (
    StageCountTestCaseError,
)
from src.dtos import (
    StagecountSpecDTO,
    TestType,
    SpecType,
    LocationDTO,
)


class TestStageCountTestCase:
    @pytest.fixture
    def spec(self) -> StagecountSpecDTO:
        return StagecountSpecDTO(
            location=LocationDTO(path="dummy://stagecount_spec"),
            testobject="stage_customers",
            spec_type=SpecType.STAGECOUNT,
            raw_file_format="csv",
            raw_file_encoding="utf-8",
            skip_lines=1,
        )

    @pytest.fixture
    def testcase(self, testcase_creator) -> AbstractTestCase:
        return testcase_creator.create(ttype=TestType.STAGECOUNT)

    def test_happy_path_counts_match(self, testcase):
        def translate_query(query, db):
            return query

        def run_query(query, db):
            return pl.DataFrame({"__cnt__": [10], "__src_path__": ["raw/data.csv"]})

        def get_testobject_rowcount(testobject, *args, **kwargs):
            return 10

        testcase.backend.translate_query = translate_query
        testcase.backend.run_query = run_query
        testcase.backend.get_testobject_rowcount = get_testobject_rowcount
        testcase.specs = []

        testcase._execute()

        assert testcase.result == testcase.result.OK
        assert "matches" in testcase.summary
        assert "stagecount_diff" not in testcase.diff

    def test_counts_mismatch_returns_nok(self, testcase):
        def translate_query(query, db):
            return query

        def run_query(query, db):
            return pl.DataFrame({"__cnt__": [10], "__src_path__": ["/raw/data.csv"]})

        def get_testobject_rowcount(testobject, *args, **kwargs):
            return 8

        testcase.backend.translate_query = translate_query
        testcase.backend.run_query = run_query
        testcase.backend.get_testobject_rowcount = get_testobject_rowcount
        testcase.specs = []

        testcase._execute()

        assert testcase.result == testcase.result.NOK
        assert "differ" in testcase.summary
        assert testcase.diff["stagecount_diff"]["stage_rowcount"] == 10
        assert testcase.diff["stagecount_diff"]["raw_file_rowcount"] == 8

    def test_with_spec_logs_encoding_and_skip_lines(self, testcase, spec):
        def translate_query(query, db):
            return query

        def run_query(query, db):
            return pl.DataFrame({"__cnt__": [5], "__src_path__": ["/raw/data.csv"]})

        def get_testobject_rowcount(*args, **kwargs):
            return 5

        testcase.backend.translate_query = translate_query
        testcase.backend.run_query = run_query
        testcase.backend.get_testobject_rowcount = get_testobject_rowcount
        testcase.specs = [spec]

        testcase._execute()

        assert testcase.result == testcase.result.OK
        details = {k: v for d in testcase.details for k, v in d.items()}
        assert details["Encoding"] == "utf-8"
        assert details["Skip lines"] == "1"

    def test_without_spec_logs_inferred(self, testcase):
        def translate_query(query, db):
            return query

        def run_query(query, db):
            return pl.DataFrame({"__cnt__": [10], "__src_path__": ["/raw/data.csv"]})

        def get_testobject_rowcount(*args, **kwargs):
            return 10

        testcase.backend.translate_query = translate_query
        testcase.backend.run_query = run_query
        testcase.backend.get_testobject_rowcount = get_testobject_rowcount
        testcase.specs = []

        testcase._execute()

        details = {k: v for d in testcase.details for k, v in d.items()}
        assert details["Encoding"] == "inferred by backend"
        assert details["Skip lines"] == "inferred by backend"

    def test_empty_source_file_path_raises(self, testcase):
        def translate_query(query, db):
            return query

        def run_query(query, db):
            return pl.DataFrame({"__cnt__": [10], "__src_path__": [None]})

        testcase.backend.translate_query = translate_query
        testcase.backend.run_query = run_query
        testcase.specs = []

        with pytest.raises(StageCountTestCaseError):
            testcase._execute()

    def test_facts_and_details_are_populated(self, testcase):
        def translate_query(query, db):
            return query

        def run_query(query, db):
            return pl.DataFrame({"__cnt__": [10], "__src_path__": ["/raw/data.csv"]})

        def get_testobject_rowcount(*args, **kwargs):
            return 10

        testcase.backend.translate_query = translate_query
        testcase.backend.run_query = run_query
        testcase.backend.get_testobject_rowcount = get_testobject_rowcount
        testcase.specs = []

        testcase._execute()

        fact_keys = [k for fact in testcase.facts for k in fact]
        assert "Source file path" in fact_keys

        detail_keys = [k for detail in testcase.details for k in detail]
        assert "Stage rowcount" in detail_keys
        assert "Raw file rowcount" in detail_keys
