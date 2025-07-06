from abc import ABC, abstractmethod

from src.dtos.reports import ReportArtifactDTO


class IReportNamingConventions(ABC):
    """
    Handles naming conventions for testcase and testrun reports, e.g. defines filenames
    of report files stored on disk.
    """

    @abstractmethod
    def filename(self, artifact: ReportArtifactDTO) -> str:
        """
        Retuns expected report name based on testreport contents.
        """
