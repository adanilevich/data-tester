from __future__ import annotations
from typing import Dict, List, Type

from src.dtos import (
    TestResultDTO,
    TestCaseResultDTO,
    TestRunResultDTO,
    ReportArtifactDTO,
    TestType,
    ArtifactType,
)
from src.report.ports import IReportFormatter, ReportFormatterError
from src.report.adapters.plugins.formatters.default import (
    IReportNamingConventions,
    IReportArtifact,
    JsonTestCaseReportFormatter,
    XlsxTestCaseDiffFormatter,
    XlsxTestRunReportFormatter,
    TxtTestCaseReportFormatter,
)


default_formatter_config ={
    ArtifactType.XLSX_TESTCASE_DIFF: XlsxTestCaseDiffFormatter,
    ArtifactType.XLSX_TESTRUN_REPORT: XlsxTestRunReportFormatter,
    ArtifactType.JSON_TESTCASE_REPORT: JsonTestCaseReportFormatter,
    ArtifactType.TXT_TESTCASE_REPORT: TxtTestCaseReportFormatter,
}


class ArtifactTypeUnknownError(ReportFormatterError):
    """"""


class DefaultReportFormatter(IReportFormatter):
    """
    Create specific report artifacts based on the global Config values. Not every format
    is supported for both TestRun and TestCase reports.
    """

    config: Dict[ArtifactType, Type[IReportArtifact]]

    def __init__(
        self,
        naming_conventions: IReportNamingConventions,
        config: Dict[ArtifactType, Type[IReportArtifact]] = default_formatter_config,
    ):
        self.config: Dict[ArtifactType, Type[IReportArtifact]] = config
        self.naming_conventions: IReportNamingConventions = naming_conventions

    def create_artifacts(
        self,
        result: TestResultDTO,
        artifact_types: List[ArtifactType],
    ) -> List[ReportArtifactDTO]:
        """
        Applies known ArtifactFormatters (as defined by config) to the provided
        test result.
            - unknown artifact types lead to ReportFormatterErrors
            - xlsx testcase diffs are only returned if COMPARE_SAMPLE NOK result provided
        Args:
            result: TestResultDTO - can be a TestRunResultDTO or TestCaseResultDTO
            artifact_types: List[ArtifactType] - list of requested
        Returns:
            List[ReportArtifactDTO]
        """

        artifacts: List[ReportArtifactDTO] = []

        for artifact_type in artifact_types:

            formatter_class = self.config.get(artifact_type)
            if formatter_class is None:
                raise ArtifactTypeUnknownError()
            formatter = formatter_class(naming_conventions=self.naming_conventions)

            if self._artifact_is_supported(result, artifact_type):
                artifact = formatter.create_artifact(result=result)
                artifacts.append(artifact)

        return artifacts

    def _artifact_is_supported(
        self,
        result: TestResultDTO,
        artifact_type: ArtifactType,
    ) -> bool:

        if isinstance(result, TestRunResultDTO):
            return True if artifact_type == ArtifactType.XLSX_TESTRUN_REPORT else False
        elif isinstance(result, TestCaseResultDTO):
            if artifact_type == ArtifactType.XLSX_TESTCASE_DIFF:
                # xlsx-testcasediff is only supported for NOK COMPARE_SAMPLE testcases
                if artifact_type == ArtifactType.XLSX_TESTCASE_DIFF:
                    if result.testtype == TestType.COMPARE_SAMPLE:
                        return True if result.result == result.result.NOK else False
                    else:
                        return False
                else:
                    return True
            else:
                return True
        else:
            msg = f"Artifact creation: Unknown test result type: {type(result)}"
            raise ValueError(msg)
