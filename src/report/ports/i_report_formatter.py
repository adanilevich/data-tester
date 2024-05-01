from abc import ABC, abstractmethod
from typing import Any, Tuple

from src.dtos import TestCaseReportDTO, TestRunReportDTO


class IReportFormatter(ABC):
    """
    Interface definition for a report formatter. Report formatters operate on Report DTOs
    and serialize the provided report to given format such that IStorage implementations
    can save the serialized version to storage.
    """

    @abstractmethod
    def format(
        self, report: TestRunReportDTO | TestCaseReportDTO, format: str
    ) -> Tuple[str, str, Any]:
        """
        Formats provided report into the requested format and updates the report object
        attributes 'format', 'content', 'content_type'.

        Args:
            report: report to be formatted as DTO
            format: report will be formatted to this format (e.g. 'xlsx').
                Formatter must know requested format and implement formatting logic.

        Returns:
            format: str requested format
            content_type: content type of report
            content: content of report, e.g. as bytes or string or dict - depending
                on the requested format. Based on the content_type report is written
                as string or bytes (or other)
        """
