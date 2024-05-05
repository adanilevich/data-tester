from abc import ABC, abstractmethod
from typing import List

from src.dtos import TestResultDTO, ArtifactTag, ReportArtifactDTO


class IReportFormatter(ABC):
    """
    Interface definition for a report formatter. Report formatters operate on Report DTOs
    and serialize the provided report to given format such that IStorage implementations
    can save the serialized version to storage.
    """

    @abstractmethod
    def format(
        self, result: TestResultDTO, tags: List[ArtifactTag]
    ) -> List[ReportArtifactDTO]:
        """
        From given testcase or testrun result, creates a list of report artifacts which
        match at least one of the requested tags.

        Args:
            result: TestCaseResultDTO or TestRunResultDTO
            tags: list of tags (ArtifactTagDTO) requested by the client

        Returns:
            List[artifact]: List of matching report artifacts
        """
