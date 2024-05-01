from src.dtos.reports import TestCaseReportDTO, TestRunReportDTO
from src.report.ports import IReportNamingConventions


class SimpleReportNamingConventions(IReportNamingConventions):
    """
    Sets testrun report filename by testrun_id and start_ts.
    Sets testcase report filename by testobject, testcase and start_ts.
    """

    def report_name(self, report: TestCaseReportDTO | TestRunReportDTO) -> str:
        format = report.report_format or "file"

        if isinstance(report, TestCaseReportDTO):
            report_name = (
                report.testobject
                + "_"
                + report.testcase
                + "_"
                + report.start_ts
                + "."
                + format
            )
        else:
            report_name = "testrun_report_" + report.start_ts + "." + format

        return report_name
