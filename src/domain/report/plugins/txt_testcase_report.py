from typing import Any, Dict, List

import yaml

from .i_report_formatter import (
    IReportFormatter,
    ReportTypeNotSupportedError,
    ReportFormatterError,
)
from src.dtos import (
    TestReportDTO,
    TestCaseReportDTO,
    ReportArtifactFormat,
    ReportArtifact,
    ReportType,
)


class TxtTestCaseReportFormatter(IReportFormatter):
    """
    Txt-based testcase report with spec filepaths and simplified
    schema diffs.
    """

    @property
    def artifact_format(self) -> ReportArtifactFormat:
        return ReportArtifactFormat.TXT

    @property
    def report_artifact(self) -> ReportArtifact:
        return ReportArtifact.REPORT

    @property
    def report_type(self) -> ReportType:
        return ReportType.TESTCASE

    def create_artifact(self, report: TestReportDTO) -> bytes:
        """
        Creates a txt-based testcase report artifact with spec filepaths
        and simplified schema diffs.
        """

        if not isinstance(report, TestCaseReportDTO):
            raise ReportTypeNotSupportedError(
                f"Txt format not supported for {report}"
            )

        exclude = {"specifications", "diff"}
        content_dict = report.to_dict(exclude=exclude, mode="json")

        # add spec filepaths (simplified from full SpecDTO)
        content_dict["specifications"] = [
            spec.display_name or spec.location.path
            for spec in report.specifications
        ]

        # for schema testcases, add simplified diff showing only differences
        if report.testtype == "SCHEMA" and report.diff:
            content_dict["diff"] = _simplify_schema_diff(report.diff)

        try:
            yaml_bytes = yaml.safe_dump(
                data=content_dict,
                default_flow_style=False,
                indent=4,
                encoding="utf-8",
            )
            return yaml_bytes
        except Exception as e:
            msg = f"Failed to convert dict to yaml bytes: {e}"
            raise ReportFormatterError(msg) from e


def _simplify_schema_diff(
    diff: Dict[str, Any],
) -> Dict[str, List[Dict[str, str]] | Dict[str, List[str]]]:
    """Extracts only the differences from a schema diff dict."""
    simplified: Dict[str, Any] = {}

    # column_diff: only NOK entries with column name + expected/actual dtype
    if "column_diff" in diff:
        nok_columns = [
            {
                "column": entry.get("expected_column")
                or entry.get("actual_column", ""),
                "expected_dtype": entry.get("expected_dtype", ""),
                "actual_dtype": entry.get("actual_dtype", ""),
            }
            for entry in diff["column_diff"]
            if entry.get("result_all") == "NOK"
        ]
        if nok_columns:
            simplified["column_diff"] = nok_columns

    # partitioning, clustering, pk: only if expected != actual
    for key in ("partitioning_diff", "clustering_diff", "pk_diff"):
        if key in diff:
            section = diff[key]
            expected = sorted(list(section.values())[0])
            actual = sorted(list(section.values())[1])
            if expected != actual:
                simplified[key] = section

    return simplified
