from abc import ABC, abstractmethod

from src.report.ports import IFormattable


class IReportFormatter(ABC):

    @abstractmethod
    def format(self, report: IFormattable, format: str):
        """
        Formats provided report into the requested format and updates the report object
        attributes 'format', 'content', 'content_type'.
        """
