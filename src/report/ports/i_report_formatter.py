from abc import ABC, abstractmethod

from src.report import AbstractReport


class IReportFormatter(ABC):

    @abstractmethod
    def format(self, report: AbstractReport, format: str):
        """
        Formats provided report into the requested format and updates the report object
        attributes 'format', 'content', 'content_type'.
        """
