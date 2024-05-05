from typing import List

from src.config import Config
from src.report.ports import (
    ISaveReportCommandHandler,
    SaveReportCommand,
    ICreateTestRunReportCommandHandler,
    CreateTestRunReportCommand,
    ICreateTestCaseReportCommandHandler,
    CreateTestCaseReportCommand,
)
from src.dtos import (
    TestCaseResultDTO,
    TestRunResultDTO,
    TestCaseReportDTO,
    TestRunReportDTO,
    ReportDTO,
    ArtifactTag,
)


class CliReportManager:
    def __init__(
        self,
        create_testcase_report_handler: ICreateTestCaseReportCommandHandler,
        create_testrun_report_handler: ICreateTestRunReportCommandHandler,
        save_report_handler: ISaveReportCommandHandler,
    ):
        self.create_testcase_report_handler = create_testcase_report_handler
        self.create_testrun_report_handler = create_testrun_report_handler
        self.save_report_handler = save_report_handler

    def create_testcase_report(self, result: TestCaseResultDTO) -> TestCaseReportDTO:
        """Creates testcase report and populates report artifacts relevant for storage"""

        command = CreateTestCaseReportCommand(
            testcase_result=result,
            tags=[ArtifactTag.storage]
        )

        report = self.create_testcase_report_handler.create(command=command)

        return report

    def create_testrun_report(self, results: List[TestCaseResultDTO]) -> TestRunReportDTO:
        """Creates testrun report and populates report artifacts relevant for storage"""

        command = CreateTestRunReportCommand(
            testrun_result=TestRunResultDTO.from_testcase_results(results),
            tags=[ArtifactTag.storage],
        )

        report = self.create_testrun_report_handler.create(command=command)

        return report

    def save_report(self, report: ReportDTO, location: str):
        """
        Saves all storage-related artifacts to subfolders of specified location.
        Subfolders are defined by GROUP_TESTREPORTS_BY in Config.
        """

        location = location + "/" if not location.endswith("/") else location

        # storage location is extended by group_by artifacts from Config
        group_by = Config().GROUP_TESTREPORTS_BY
        for item in group_by:
            if item == "date":
                location += "/" + report.start_ts.strftime("%Y-%m-%d")
            if item in report.model_fields:
                location += "/" + report.to_dict()[item]

        command = SaveReportCommand(
            report=report, location=location, tags=[ArtifactTag.storage]
        )

        self.save_report_handler.save(command=command)
