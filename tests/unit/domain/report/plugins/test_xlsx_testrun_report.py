import io

import pytest
import polars as pl

from src.domain.report.plugins import (
    XlsxTestRunReportFormatter,
    ReportTypeNotSupportedError,
)
from src.dtos import (
    TestRunReportDTO,
    TestCaseReportDTO,
    ReportArtifactFormat,
    ReportArtifact,
    ReportType,
)

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
        # given an XlsxTestRunReportFormatter instance
        formatter = XlsxTestRunReportFormatter()
        # then artifact_format should be XLSX
        assert formatter.artifact_format == ReportArtifactFormat.XLSX
        # then report_artifact should be REPORT
        assert formatter.report_artifact == ReportArtifact.REPORT
        # then report_type should be TESTRUN
        assert formatter.report_type == ReportType.TESTRUN

    def test_create_artifact_with_valid_testrun_report(
        self, testrun_report: TestRunReportDTO
    ):
        # given a TestRunReportDTO with testcase results
        formatter = XlsxTestRunReportFormatter()
        # when create_artifact is called
        result = formatter.create_artifact(testrun_report)
        # then it should return valid Excel bytes
        assert isinstance(result, bytes)
        assert len(result) > 0

        excel_io = io.BytesIO(result)
        df = pl.read_excel(excel_io)

        # then it should have only the important columns
        for col in EXPECTED_COLUMNS:
            assert col in df.columns

        # and should NOT have excluded columns
        for col in EXCLUDED_COLUMNS:
            assert col not in df.columns

        # and it should have the correct number of rows
        assert df.shape[0] == len(testrun_report.testcase_results)

        # and the data should match the original testcase results
        for i, testcase_result in enumerate(testrun_report.testcase_results):
            assert df["result"][i] == str(testcase_result.result)
            assert df["testtype"][i] == str(testcase_result.testtype)
            assert df["summary"][i] == testcase_result.summary

    def test_manually_check_artifact(self, testrun_report: TestRunReportDTO):
        # Use this testcase to manually check the artifact using breakpoints
        # IMPORTANT: don't stop debug session otherwise file is not deleted
        formatter = XlsxTestRunReportFormatter()
        # when artifact is created
        result = formatter.create_artifact(testrun_report)

        # then it should return valid Excel bytes
        assert isinstance(result, bytes)
        assert len(result) > 0

    def test_create_artifact_with_testcase_report_raises_error(
        self, testcase_report: TestCaseReportDTO
    ):
        # given an XlsxTestRunReportFormatter and a TestCaseReportDTO (invalid type)
        formatter = XlsxTestRunReportFormatter()
        # when create_artifact is called with wrong type
        with pytest.raises(ReportTypeNotSupportedError) as exc_info:
            formatter.create_artifact(testcase_report)
        # then it should raise ReportTypeNotSupportedError
        assert "Can't create testrun report from a TestCaseReportDTO object" in str(
            exc_info.value
        )

    def test_create_artifact_with_empty_testcase_results(
        self, testrun_report: TestRunReportDTO
    ):
        # given a TestRunReportDTO with empty testcase_results
        formatter = XlsxTestRunReportFormatter()
        testrun_report.testcase_results = []
        # when create_artifact is called
        result = formatter.create_artifact(testrun_report)
        # then it should return valid Excel bytes (empty DataFrame)
        assert isinstance(result, bytes)
        assert len(result) > 0

        # Use BytesIO to verify the Excel content
        excel_io = io.BytesIO(result)
        # Handle empty DataFrame case
        try:
            df = pl.read_excel(excel_io)
        except pl.exceptions.NoDataError:
            # Empty Excel file - this is expected for empty DataFrame
            return

        # Should have expected columns but no rows
        for col in EXPECTED_COLUMNS:
            assert col in df.columns
        assert df.shape[0] == 0

    def test_excel_content_structure(self, testrun_report: TestRunReportDTO):
        # given a TestRunReportDTO with multiple testcase results
        formatter = XlsxTestRunReportFormatter()
        # when create_artifact is called
        result = formatter.create_artifact(testrun_report)

        # then the Excel content should be properly structured
        excel_io = io.BytesIO(result)
        df = pl.read_excel(excel_io)

        # Verify data types and structure
        assert df["result"].dtype == pl.Utf8
        assert df["testtype"].dtype == pl.Utf8
        assert df["summary"].dtype == pl.Utf8
        assert df["domain"].dtype == pl.Utf8
        assert df["testobject"].dtype == pl.Utf8
