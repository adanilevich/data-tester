from typing import Any, Dict, List

import yaml

from src.dtos import (
    ReportArtifact,
    ReportArtifactFormat,
    TestCaseDTO,
)

from .i_report_formatter import (
    ITestCaseFormatter,
    ReportFormatterError,
)


class TxtTestCaseReportFormatter(ITestCaseFormatter):
    """
    Txt-based testcase report with spec filepaths and simplified
    schema diffs.
    """

    @property
    def artifact_format(self) -> ReportArtifactFormat:
        return ReportArtifactFormat.TXT

    @property
    def artifact(self) -> ReportArtifact:
        return ReportArtifact.REPORT

    def create_artifact(self, testcase: TestCaseDTO) -> bytes:
        """
        Creates a txt-based testcase report artifact with spec filepaths
        and simplified schema diffs.
        """
        exclude = {"specs", "diff", "domain_config"}
        content_dict = testcase.to_dict(exclude=exclude, mode="json")

        # convert enum values to strings
        content_dict["result"] = testcase.result.value
        content_dict["status"] = testcase.status.value
        content_dict["testtype"] = testcase.testtype.value
        content_dict["testobject"] = testcase.testobject.name

        # add spec filepaths (simplified from full SpecDTO)
        content_dict["specs"] = [
            spec.display_name or spec.location.path for spec in testcase.specs
        ]

        # for schema testcases, add simplified diff showing only differences
        if testcase.testtype.value == "SCHEMA" and testcase.diff:
            content_dict["diff"] = _simplify_schema_diff(testcase.diff)

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
                "column": entry.get("expected_column") or entry.get("actual_column", ""),
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
