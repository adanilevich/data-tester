import io

import polars as pl

from src.domain.report.plugins import XlsxTestRunReportFormatter
from src.dtos import ReportArtifactFormat, TestRunDTO

EXPECTED_COLUMNS = [
    "domain",
    "stage",
    "instance",
    "testobject",
    "testtype",
    "result",
    "summary",
]

EXCLUDED_COLUMNS = [
    "report_id",
    "testrun_id",
    "testset_id",
    "labels",
    "start_ts",
    "end_ts",
]


class TestXlsxTestRunReportFormatter:
    def test_properties(self):
        formatter = XlsxTestRunReportFormatter()
        assert formatter.artifact_format == ReportArtifactFormat.XLSX

    def test_create_artifact_with_valid_testrun(self, testrun: TestRunDTO):
        formatter = XlsxTestRunReportFormatter()
        result = formatter.create_artifact(testrun)

        assert isinstance(result, bytes)
        assert len(result) > 0

        excel_io = io.BytesIO(result)
        df = pl.read_excel(excel_io)

        for col in EXPECTED_COLUMNS:
            assert col in df.columns

        for col in EXCLUDED_COLUMNS:
            assert col not in df.columns

        assert df.shape[0] == len(testrun.results)

        for i, tc in enumerate(testrun.results):
            assert df["result"][i] == tc.result.value
            assert df["testtype"][i] == tc.testtype.value
            assert df["summary"][i] == tc.summary

    def test_create_artifact_with_empty_results(self, testrun: TestRunDTO):
        formatter = XlsxTestRunReportFormatter()
        empty_testrun = testrun.model_copy(update={"results": []})
        result = formatter.create_artifact(empty_testrun)

        assert isinstance(result, bytes)
        assert len(result) > 0

        excel_io = io.BytesIO(result)
        try:
            df = pl.read_excel(excel_io)
        except pl.exceptions.NoDataError:
            return

        for col in EXPECTED_COLUMNS:
            assert col in df.columns
        assert df.shape[0] == 0

    def test_excel_content_structure(self, testrun: TestRunDTO):
        formatter = XlsxTestRunReportFormatter()
        result = formatter.create_artifact(testrun)

        excel_io = io.BytesIO(result)
        df = pl.read_excel(excel_io)

        assert df["result"].dtype == pl.Utf8
        assert df["testtype"].dtype == pl.Utf8
        assert df["summary"].dtype == pl.Utf8
        assert df["domain"].dtype == pl.Utf8
        assert df["testobject"].dtype == pl.Utf8
