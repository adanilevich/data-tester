import pytest
from src.report import TestCaseReport
from src.dtos import TestCaseResultDTO, TestCaseReportDTO


class TestTestCaseReport:

    def test_initializing_report_from_testcase_result(
        self, formatter, naming_conventions, storage, testcase_result: TestCaseResultDTO):

        # given a valid testcase result
        testcase_result = testcase_result

        # when valid formatter, storage and naming conventions are provided
        report = TestCaseReport.from_testcase_result(
            testcase_result=testcase_result,
            formatter=formatter,
            storage=storage,
            naming_conventions=naming_conventions
        )

        # then a valid, unformatted TestCaseReport is initialized
        assert isinstance(report, TestCaseReport)
        assert report.format is None
        assert report.content_type is None
        assert report.content is None
        assert isinstance(report.to_dto(), TestCaseReportDTO)

    def test_report_formatter_is_applied(self, testcase_report: TestCaseReport):

        # given an initialized testcase report with a dummy formatter
        report = testcase_report

        # when report is formatted in a specified format
        format = "my_format"
        formatted = report.format_report(format=format)

        # then format, content and content_type are set correctly
        assert isinstance(formatted, TestCaseReport)
        assert formatted.format == report.formatter._format  # type: ignore
        assert formatted.content == report.formatter._content  # type: ignore
        assert formatted.content_type == report.formatter._content_type  # type: ignore


    def test_that_unformatted_report_cant_be_saved(self, testcase_report: TestCaseReport):

        # given an initialized testcase report with a dummy formatter
        report = testcase_report

        # when report is not formatted
        report.format = None

        # then saving the report raises an error
        with pytest.raises(ValueError):
            report.save_report(location="my_location")


    def test_that_formatted_report_is_saved(self, testcase_report: TestCaseReport):

        # given an initialized testcase report with a dummy formatter
        report = testcase_report

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
