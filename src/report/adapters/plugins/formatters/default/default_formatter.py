from __future__ import annotations
from typing import Dict, List, Type

from src.dtos import (
    TestResultDTO,
    TestCaseResultDTO,
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
    Factory class to create and apply specific formatters. Content types declare which
    report formats are known and corresponding content types. Not every format is
    supported for both TestRun and TestCase reports. See specific formatters below.
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
        """

        artifacts: List[ReportArtifactDTO] = []

        for artifact_type in artifact_types:

            formatter_cls = self.config.get(artifact_type)
            if formatter_cls is None:
                raise ArtifactTypeUnknownError()
            formatter = formatter_cls(naming_conventions=self.naming_conventions)

            if self._diff_is_only_requested_for_nok_compare_sample(result, artifact_type):
                artifact = formatter.create_artifact(result=result)
                artifacts.append(artifact)

        return artifacts

    def _diff_is_only_requested_for_nok_compare_sample(
        self,
        result: TestResultDTO,
        artifact_type: ArtifactType,
    ) -> bool:

        # xlsx-testcasediff is only supported for COMPARE_SAMPLE testcases with NOK result
        if not artifact_type == ArtifactType.XLSX_TESTCASE_DIFF:
            return True

        if not isinstance(result, TestCaseResultDTO):
            return False

        if not result.testtype == TestType.COMPARE_SAMPLE:
            return False

        if not result.result == result.result.NOK:
            return False
        else:
            return True
