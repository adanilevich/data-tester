from abc import ABC, abstractmethod

from src.dtos.reports import TestCaseReportDTO, TestRunReportDTO


class IReportNamingConventions(ABC):
    """
    Handles naming conventions for testcase and testrun reports, e.g. defines filenames
    of report files stored on disk.
    """

    @abstractmethod
    def report_name(self, report: TestCaseReportDTO | TestRunReportDTO) -> str:
        """
        Retuns expected report name based on testreport contents.
        """
