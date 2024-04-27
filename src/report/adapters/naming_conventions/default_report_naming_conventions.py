from src.dtos.reports import TestCaseReportDTO, TestRunReportDTO
from src.report.ports import IReportNamingConventions


class DefaultReportNamingConventions(IReportNamingConventions):

    def report_name(self, report: TestCaseReportDTO | TestRunReportDTO) -> str:

        if isinstance(report, TestCaseReportDTO):
            format = report.format or ".file"
            report_name = report.testobject + "_" \
                + report.testcase + "_" \
                + report.start \
                + "." + format
        else:
            report_name = "testrun_report_" + report.start + ".xlsx"

        return report_name
