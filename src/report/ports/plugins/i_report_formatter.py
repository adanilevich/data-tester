from abc import ABC, abstractmethod
from typing import List
from src.dtos import TestResultDTO, ReportArtifactDTO, ArtifactType


class ReportFormatterError(Exception):
    """"""


class IReportFormatter(ABC):
    """
    Interface definition for a report formatter. Report formatters operate on Report DTOs
    and serialize the provided report to given format such that IStorage implementations
    can save the serialized version to storage.
    """

    @abstractmethod
    def create_artifacts(
        self,
        result: TestResultDTO,
        artifact_types: List[ArtifactType],
    ) -> List[ReportArtifactDTO]:
        """
        From given testcase or testrun result, creates a list of requestd report
        artifacts.

        Args:
            result: TestCaseResultDTO or TestRunResultDTO
            artifact_types: list of requested artifact types to be created

        Returns:
            List[artifact]: List of matching report artifacts

        Raises:
            ReportFormatterError
        """
