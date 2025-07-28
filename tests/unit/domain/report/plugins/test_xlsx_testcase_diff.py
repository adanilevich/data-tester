import io
import pathlib

import pytest
import polars as pl

from src.domain.report.plugins import (
    XlsxTestCaseDiffFormatter,
    ReportTypeNotSupportedError,
    ReportFormatterError,
)
from src.dtos import (
    TestCaseReportDTO,
    TestRunReportDTO,
    ReportArtifactFormat,
    ReportArtifact,
    ReportType,
)


class TestXlsxTestCaseDiffFormatter:
    def test_properties(self):
        # given an XlsxTestCaseDiffFormatter instance
        formatter = XlsxTestCaseDiffFormatter()
        # then artifact_format should be XLSX
        assert formatter.artifact_format == ReportArtifactFormat.XLSX
        # then report_artifact should be DIFF
        assert formatter.report_artifact == ReportArtifact.DIFF
        # then report_type should be TESTCASE
        assert formatter.report_type == ReportType.TESTCASE

    def test_create_artifact_with_valid_testcase_report_with_diff(
        self, testcase_report: TestCaseReportDTO
    ):
        # given a TestCaseReportDTO with non-empty diff
        formatter = XlsxTestCaseDiffFormatter()
        testcase_report.diff = {
            "compare_diff": {"a": [1, 2, 3], "b": ["ab", "bb", "df"]},
            "another_diff": {"x": [10, 20], "y": ["test1", "test2"]},
        }
        # when create_artifact is called
        result = formatter.create_artifact(testcase_report)
        # then it should return valid Excel bytes
        assert isinstance(result, bytes)
        assert len(result) > 0

        # Use BytesIO to avoid writing to disk
        excel_io = io.BytesIO(result)

        # Then compare sheet should exist
        sheet_name = "compare_diff"
        df_compare = pl.read_excel(excel_io, sheet_name=sheet_name)

        # And it should have the correct columns and values
        assert list(getattr(df_compare, "columns", [])) == ["a", "b"]
        assert df_compare.shape == (3, 2)
        assert df_compare["a"].to_list() == [1, 2, 3]
        assert df_compare["b"].to_list() == ["ab", "bb", "df"]

        # Then another_diff sheet should exist
        sheet_name = "another_diff"
        df_another = pl.read_excel(excel_io, sheet_name=sheet_name)

        # And it should have the correct columns and values
        assert list(getattr(df_another, "columns", [])) == ["x", "y"]
        assert df_another.shape == (2, 2)
        assert df_another["x"].to_list() == [10, 20]
        assert df_another["y"].to_list() == ["test1", "test2"]

    def test_manually_check_artifact(self, testcase_report: TestCaseReportDTO):
        # Use this testcase to manually check the artifact using breakpoints
        # IMPORTANT: don't stop debug session otherwise file is not deleted
        formatter = XlsxTestCaseDiffFormatter()
        testcase_report.diff = {
            "sheet1": {"col1": [1, 2, 3], "col2": ["a", "b", "c"]},
            "sheet2": {"col3": [4, 5], "col4": ["d", "e"]},
            "sheet3": {"col5": [6, 7, 8], "col6": ["f", "g", "h"]},
        }
        # when artifact is created
        result = formatter.create_artifact(testcase_report)

        # then it should return valid Excel bytes
        assert isinstance(result, bytes)
        assert len(result) > 0

        TEST_DIR = pathlib.Path(__file__).parent
        OUTPUT_FILE = TEST_DIR / "test_artifact.xlsx"
        with open(OUTPUT_FILE, "wb") as f:
            f.write(result)
            pathlib.Path.unlink(OUTPUT_FILE)

    def test_create_artifact_with_testrun_report_raises_error(
        self, testrun_report: TestRunReportDTO
    ):
        # given an XlsxTestCaseDiffFormatter and a TestRunReportDTO (invalid type)
        formatter = XlsxTestCaseDiffFormatter()
        # when create_artifact is called with wrong type
        with pytest.raises(ReportTypeNotSupportedError) as exc_info:
            formatter.create_artifact(testrun_report)
        # then it should raise ReportTypeNotSupportedError
        assert "Xlsx diff not supported" in str(exc_info.value)

    def test_create_artifact_with_empty_diff_raises_error(
        self, testcase_report: TestCaseReportDTO
    ):
        # given a TestCaseReportDTO with empty diff
        formatter = XlsxTestCaseDiffFormatter()
        testcase_report.diff = {}
        # when create_artifact is called with empty diff
        with pytest.raises(ReportFormatterError) as exc_info:
            formatter.create_artifact(testcase_report)
        # then it should raise ReportFormatterError
        assert "No diff to create artifact for" in str(exc_info.value)
