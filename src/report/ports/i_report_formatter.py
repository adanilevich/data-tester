from abc import ABC, abstractmethod

from src.dtos import TestCaseReportDTO, TestRunReportDTO


class IReportFormatter(ABC):

    @abstractmethod
    def format_testcase_report(self, report: TestCaseReportDTO,
                               format: str) -> TestCaseReportDTO:
        """
        Formats provided report into the requested format.
        For each specified format, a formatter must be implemented.
        """

    @abstractmethod
    def format_testrun_report(self, report: TestRunReportDTO,
                              format: str) -> TestRunReportDTO:
        """
        Formats provided report into the requested format.
        For each specified format, a formatter must be implemented.
        """
