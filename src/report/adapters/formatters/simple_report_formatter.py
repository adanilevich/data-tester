from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Dict, Tuple
from io import BytesIO

import polars as pl
import yaml  # type: ignore

from src.dtos import TestCaseReportDTO, TestRunReportDTO
from src.report.ports import IReportFormatter


class SimpleReportFormatter(IReportFormatter):
    """
    Factory class to create and apply specific formatters. Content types declare which
    report formats are known and corresponding content types. Not every format is
    supported for both TestRun and TestCase reports. See specific formatters below.
    """

    content_types: Dict[str, str] = {
        "xlsx": "application/vnd.opnexmlformats-officedocument.spreadsheetml.template",
        "txt": "text/plain",
        "dict": "application/json",
    }

    def _get_formatter(
        self, format: str, report: TestRunReportDTO | TestCaseReportDTO
    ) -> AbstractFormatter:
        formatter: AbstractFormatter

        if format == "xlsx":
            formatter = XlsxTestRunReportFormatter()
        elif format == "dict":
            formatter = DictReportFormatter()
        elif format == "txt":
            formatter = TxtTestCaseReportFormatter()

        return formatter

    def format(
        self, report: TestRunReportDTO | TestCaseReportDTO, format: str
    ) -> Tuple[str, str, Any]:
        if format not in self.content_types.keys():
            raise ValueError(f"Report format not supported: {format}")

        formatter = self._get_formatter(format=format, report=report)
        content = formatter.format(report=report)

        return format, self.content_types[format], content


class AbstractFormatter(ABC):
    @abstractmethod
    def format(self, report: TestCaseReportDTO | TestRunReportDTO) -> Any:
        """Abstract class for format-specific formatters"""


class DictReportFormatter(AbstractFormatter):
    def format(self, report: TestRunReportDTO | TestCaseReportDTO) -> Any:
        return report.to_dict()


class XlsxTestRunReportFormatter(AbstractFormatter):
    def format(self, report: TestRunReportDTO | TestCaseReportDTO) -> bytes:
        if not isinstance(report, TestRunReportDTO):
            raise ValueError("xlsx formatting only supported for testrun reports")

        results = [result.to_dict() for result in report.testcase_results]
        df = pl.DataFrame(results)
        io = BytesIO()
        df.write_excel(io)

        return io.getbuffer().tobytes()


class TxtTestCaseReportFormatter(AbstractFormatter):
    def format(self, report: TestCaseReportDTO | TestRunReportDTO) -> str:
        if not isinstance(report, TestCaseReportDTO):
            raise ValueError("txt formatting only supported for testcase reports.")

        return yaml.safe_dump(data=report.to_dict(), default_flow_style=None, indent=4)
