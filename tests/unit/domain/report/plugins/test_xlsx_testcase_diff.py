import io
import pathlib

import polars as pl
import pytest

from src.domain.report.plugins import (
    ReportFormatterError,
    XlsxTestCaseDiffFormatter,
)
from src.dtos import ReportArtifact, ReportArtifactFormat, TestCaseDTO


class TestXlsxTestCaseDiffFormatter:
    def test_properties(self):
        formatter = XlsxTestCaseDiffFormatter()
        assert formatter.artifact_format == ReportArtifactFormat.XLSX
        assert formatter.artifact == ReportArtifact.DIFF

    def test_create_artifact_with_valid_diff(self, testcase_result: TestCaseDTO):
        formatter = XlsxTestCaseDiffFormatter()
        tc = testcase_result.model_copy(
            update={
                "diff": {
                    "compare_diff": {"a": [1, 2, 3], "b": ["ab", "bb", "df"]},
                    "another_diff": {"x": [10, 20], "y": ["test1", "test2"]},
                }
            }
        )
        result = formatter.create_artifact(tc)

        assert isinstance(result, bytes)
        assert len(result) > 0

        excel_io = io.BytesIO(result)

        df_compare = pl.read_excel(excel_io, sheet_name="compare_diff")
        assert list(df_compare.columns) == ["a", "b"]
        assert df_compare.shape == (3, 2)
        assert df_compare["a"].to_list() == [1, 2, 3]
        assert df_compare["b"].to_list() == ["ab", "bb", "df"]

        df_another = pl.read_excel(excel_io, sheet_name="another_diff")
        assert list(df_another.columns) == ["x", "y"]
        assert df_another.shape == (2, 2)
        assert df_another["x"].to_list() == [10, 20]
        assert df_another["y"].to_list() == ["test1", "test2"]

    def test_manually_check_artifact(self, testcase_result: TestCaseDTO):
        formatter = XlsxTestCaseDiffFormatter()
        tc = testcase_result.model_copy(
            update={
                "diff": {
                    "sheet1": {"col1": [1, 2, 3], "col2": ["a", "b", "c"]},
                    "sheet2": {"col3": [4, 5], "col4": ["d", "e"]},
                    "sheet3": {"col5": [6, 7, 8], "col6": ["f", "g", "h"]},
                }
            }
        )
        result = formatter.create_artifact(tc)

        assert isinstance(result, bytes)
        assert len(result) > 0

        TEST_DIR = pathlib.Path(__file__).parent
        OUTPUT_FILE = TEST_DIR / "test_artifact.xlsx"
        with open(OUTPUT_FILE, "wb") as f:
            f.write(result)
            pathlib.Path.unlink(OUTPUT_FILE)

    def test_create_artifact_with_empty_diff_raises_error(
        self, testcase_result: TestCaseDTO
    ):
        formatter = XlsxTestCaseDiffFormatter()
        tc = testcase_result.model_copy(update={"diff": {}})
        with pytest.raises(ReportFormatterError) as exc_info:
            formatter.create_artifact(tc)
        assert "No diff to create artifact for" in str(exc_info.value)
