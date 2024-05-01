from typing import Any, List, Self
from abc import ABC, abstractmethod

from src.report.ports import IReportFormatter, IStorage, IReportNamingConventions


class AbstractReport(ABC):
    """
    Abstact report class from which TestRunReport and TestCaseReport inherit.
    Bundles common functions like saving and formatting reports.
    """

    def __init__(
        self,
        report_format: str | None = None,
        content_type: str | None = None,
        content: Any = None,
    ):
        self.report_format: str | None = report_format
        self.content_type: str | None = content_type
        self.content: Any = content

    def format(self, format: str, formatter: IReportFormatter) -> Self:
        """
        Applies provided formatter to format the report and set content attributes
        """

        dto = self.to_dto()
        format, content_type, content = formatter.format(report=dto, format=format)
        self.report_format = format
        self.content_type = content_type
        self.content = content

        return self

    def save(
        self,
        location,
        naming_conventions: IReportNamingConventions,
        storage: IStorage,
        group_by: List[str] | None = None,
    ):
        """
        Uses storage object to save report to report storage. Provided naming conventions
        are applied e.g. to derive target filename.

        Args:
            location: path, e.g. folder where to save report to
            naming_conventions: a naming conventions object which derives target filename
                based on report attributes
            storage: storage adapter which stores the report, e.g. to disk or S3
            group_by: list of report attributes which are used as subfolder structure
                under the path defined by 'location', e.g.
                    'testrun_id': groups reports in folders named by testrun_id
                    'date': groups reports in folders by date
        """

        group_by = group_by or []

        if self.report_format is None:
            raise ValueError("Report must be formatted and the applied format specified.")

        if self.content_type is None:
            raise ValueError("Content type of report to be saved must be defined.")

        if self.content is None:
            raise ValueError("Content of report must be non-empty in order to save.")

        # TODO: if groupby = date, then extract date from start_ts
        if group_by is not None:
            for item in group_by:
                dto_ = self.to_dto()
                dict_ = dto_.to_dict()
                if item in dto_.model_fields:
                    location += "/" + str(dict_[item])

        filename = location + "/" + naming_conventions.report_name(self.to_dto())

        storage.write(content=self.content, content_type=self.content_type, path=filename)

    @abstractmethod
    def to_dto(self):
        """Subclasses TestRunReport and TestCaseReport must implement this method"""
