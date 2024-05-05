from __future__ import annotations
from typing import Dict, List, Type
from pydantic import BaseModel

from src.dtos import (
    TestResultDTO,
    TestCaseResultDTO,
    TestRunResultDTO,
    ReportArtifactDTO,
    ArtifactTag,
    TestType,
)
from src.report.ports import IReportFormatter
from src.report.plugins import (
    IReportNamingConventions,
    IReportArtifact,
    JsonTestCaseReportFormatter,
    XlsxTestCaseDiffFormatter,
    XlsxTestRunReportFormatter,
    TxtTestCaseReportFormatter,
)


class ArtifactConfig(BaseModel):
    tags: List[ArtifactTag]
    supported_result_type: Type[TestResultDTO]
    formatter: Type[IReportArtifact]


class FormatterConfig(BaseModel):
    artifact_types: Dict[str, ArtifactConfig]


default_config = FormatterConfig(
    artifact_types={
        "xlsx-testcase-diff": ArtifactConfig(
            tags=[ArtifactTag.storage],
            supported_result_type=TestCaseResultDTO,
            formatter=XlsxTestCaseDiffFormatter,
        ),
        "xlsx-testrun-report": ArtifactConfig(
            tags=[ArtifactTag.storage],
            supported_result_type=TestRunResultDTO,
            formatter=XlsxTestRunReportFormatter,
        ),
        "json-testcase-report": ArtifactConfig(
            tags=[ArtifactTag.ui],
            supported_result_type=TestCaseResultDTO,
            formatter=JsonTestCaseReportFormatter,
        ),
        "txt-testcase-report": ArtifactConfig(
            tags=[ArtifactTag.storage],
            supported_result_type=TestCaseResultDTO,
            formatter=TxtTestCaseReportFormatter,
        ),
    }
)


class DefaultReportFormatter(IReportFormatter):
    """
    Factory class to create and apply specific formatters. Content types declare which
    report formats are known and corresponding content types. Not every format is
    supported for both TestRun and TestCase reports. See specific formatters below.
    """

    config: FormatterConfig

    def __init__(
        self,
        naming_conventions: IReportNamingConventions,
        config: FormatterConfig = default_config,
    ):
        self.config: FormatterConfig = config
        self.naming_conventions: IReportNamingConventions = naming_conventions

    def format(
        self, result: TestResultDTO, tags: List[ArtifactTag]
    ) -> List[ReportArtifactDTO]:
        artifacts: List[ReportArtifactDTO] = []

        for artifact_type, artifact_config in self.config.artifact_types.items():
            if all(
                [
                    self._artifact_type_is_supported_for_result_type(
                        artifact_config, result
                    ),
                    self._requested_tags_match_artifact_tags(tags, artifact_config),
                    self._result_is_testcase_result_for_compare_sample(
                        result, artifact_type
                    ),
                ]
            ):
                formatter = self._formatter(artifact_type=artifact_type)
                artifact = formatter.format(result=result)
                artifacts.append(artifact)

        return artifacts

    def _formatter(self, artifact_type: str) -> IReportArtifact:
        if artifact_type not in self.config.artifact_types:
            raise ValueError("Unknown artifact type")

        artifact_config = self.config.artifact_types[artifact_type]
        return artifact_config.formatter(naming_conventions=self.naming_conventions)

    def _artifact_type_is_supported_for_result_type(
        self, artifact_config: ArtifactConfig, result: TestResultDTO
    ) -> bool:
        if isinstance(result, artifact_config.supported_result_type):
            return True
        else:
            return False

    def _requested_tags_match_artifact_tags(
        self, tags: List[ArtifactTag], artifact_config: ArtifactConfig
    ) -> bool:
        if len(list(set(tags) & set(artifact_config.tags))) > 0:
            return True
        else:
            return False

    def _result_is_testcase_result_for_compare_sample(
        self, result: TestResultDTO, artifact_type
    ) -> bool:
        # xlsx-testcasediff is only supported for COMPARE_SAMPLE testcases with NOK result

        if not artifact_type == "xlsx-testcase-diff":
            return True

        if not isinstance(result, TestCaseResultDTO):
            return False

        if not result.testtype == TestType.COMPARE_SAMPLE:
            return False

        if not result.result == result.result.NOK:
            return False
        else:
            return True
