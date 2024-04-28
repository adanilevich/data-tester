from abc import ABC, abstractmethod
from typing import Any

from src.dtos import TestCaseReportDTO, TestRunReportDTO


class IFormattable(ABC):
    """
    Defines formal interface between IFormatter and (Abstract)Report.
    This is defined to prevent circular imports since Formatters and Reports depend
    on each other
    """

    format: str | None
    content_type: str | None
    content: Any

    @abstractmethod
    def to_dto(self) -> TestRunReportDTO | TestCaseReportDTO:
        """Returns itself as DTO"""
