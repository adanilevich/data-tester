from src.report import TestRunReport
from src.dtos import TestRunResultDTO, TestRunReportDTO, TestCaseResultDTO


class TestTestRunReport:

    def test_initializing_report_from_testcase_results(
        self, formatter, naming_conventions, storage, testcase_result: TestCaseResultDTO):

        # given a valid testcase result
        testcase_results = [testcase_result, testcase_result]

        # when valid formatter, storage and naming conventions are provided
        report = TestRunReport.from_testrun_result(
            testrun_result=TestRunResultDTO.from_testcase_results(
                testcase_results=testcase_results),
            formatter=formatter,
            storage=storage,
            naming_conventions=naming_conventions
        )

        # then a valid, unformatted TestCaseReport is initialized
        assert isinstance(report, TestRunReport)
        assert report.format is None
        assert report.content_type is None
        assert report.content is None
        assert len(report.testcase_results) == 2
        assert isinstance(report.to_dto(), TestRunReportDTO)


    def test_that_formatted_report_is_saved(self, testrun_report: TestRunReport):

        # given an initialized testcase report with a dummy formatter
        report = testrun_report

        # when report is formatted in a specified format
        format = "my_format"
        _ = report.format_report(format=format)

        # and report is saved by testrun_id and start_ts
        report.save_report(location="any_location", group_by=["testrun_id", "start_ts"])

        # then it is written to specified location
        written_locations = report.storage.written  # type: ignore
        testrun_id = report.testrun_id
        start_ts = report.start_ts
        assert f"any_location/{testrun_id}/{start_ts}/report" in written_locations
