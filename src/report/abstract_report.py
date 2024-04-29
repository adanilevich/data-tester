from typing import Any, List, Self
from src.report.ports import (
    IFormattable, IReportFormatter, IStorage, IReportNamingConventions
)


class AbstractReport(IFormattable):

    def __init__(self, formatter: IReportFormatter, storage: IStorage,
                 naming_conventions: IReportNamingConventions,
                 format: str | None = None, content_type: str | None = None,
                 content: Any = None):

        self.formatter: IReportFormatter = formatter
        self.storage: IStorage = storage
        self.format: str | None = format
        self.content_type: str | None = content_type
        self.content: Any = content
        self.naming_conventions: IReportNamingConventions = naming_conventions

    def format_report(self, format: str) -> Self:

        self.formatter.format(report=self, format=format)

        return self

    def save_report(self, location, group_by: List[str] | None = None,):

        group_by = group_by or []

        if self.format is None:
            raise ValueError("Report must be formatted and the applied format specified.")

        if self.content_type is None:
            raise ValueError("Content type of report to be saved must be defined.")

        if self.content is None:
            raise ValueError("Content of report must be non-empty in order to save.")

        if group_by is not None:
            for item in group_by:
                dto_ = self.to_dto()
                dict_ = dto_.to_dict()
                if item in dto_.model_fields:
                    location += "/" + str(dict_[item])

        filename = location + "/" + self.naming_conventions.report_name(self.to_dto())

        self.storage.write(
            content=self.content,
            content_type=self.content_type,
            path=filename
        )

    def to_dto(self):
        """Subclasses TestRunReport and TestCaseReport must implement this method"""
        raise NotImplementedError("to_dto must be implemented by Report subclasses.")
