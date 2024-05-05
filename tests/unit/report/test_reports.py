# from typing import Any, List, Tuple
# import pytest
# from src.report import TestCaseReport, TestRunReport
# from src.dtos import (
#     TestCaseResultDTO,
#     TestCaseReportDTO,
#     TestRunResultDTO,
#     TestRunReportDTO,
# )
# from src.report.ports import IReportFormatter, IStorage, IReportNamingConventions


# class DummyFormatter(IReportFormatter):
#     def __init__(self):
#         self.report_format = None
#         self.content = None
#         self.content_type = None

#     def format(
#         self, report: TestCaseReportDTO | TestRunReportDTO, format: str
#     ) -> Tuple[str, str, str]:
#         self.report_format = format
#         self.content = format
#         self.content_type = format

#         return self.report_format, self.content_type, self.content


# class DummyStorage(IStorage):
#     def __init__(self):
#         self.written: List[str] = []

#     def write(
#         self, content: Any, path: str, content_type: str, encoding: str | None = None
#     ):
#         self.written.append(path)


# class DummyNamingConventions(IReportNamingConventions):
#     def report_name(self, *args, **kwargs) -> str:
#         return "report"


# @pytest.fixture
# def testcase_report(testcase_result) -> TestCaseReport:
#     return TestCaseReport.from_testcase_result(
#         testcase_result=testcase_result,
#     )


# @pytest.fixture
# def testrun_report(testcase_result) -> TestRunReport:
#     return TestRunReport.from_testrun_result(
#         testrun_result=TestRunResultDTO.from_testcase_results(
#             testcase_results=[testcase_result, testcase_result]
#         ),
#     )


# class TestTestCaseReport:
#     def test_initializing_report_from_testcase_result(
#         self, testcase_result: TestCaseResultDTO
#     ):
#         # given a valid testcase result
#         testcase_result = testcase_result

#         # when a report from this result is created
#         report = TestCaseReport.from_testcase_result(testcase_result=testcase_result)

#         # then the report a valid, unformatted TestCaseReport
#         assert isinstance(report, TestCaseReport)
#         assert report.report_format is None
#         assert report.content_type is None
#         assert report.content is None
#         assert isinstance(report.to_dto(), TestCaseReportDTO)

#     def test_that_report_is_correctly_formatted(self, testcase_report: TestCaseReport):
#         # given an initialized testcase report
#         report = testcase_report

#         # when report is formatted in a specified format
#         format = "my_format"
#         formatter = DummyFormatter()
#         #formatted = report.create_artifacts(format=format, formatter=formatter)

#         # then format, content and content_type are set correctly
#         assert isinstance(formatted, TestCaseReport)
#         assert formatted.report_format == formatter.report_format  # type: ignore
#         assert formatted.content == formatter.content  # type: ignore
#         assert formatted.content_type == formatter.content_type  # type: ignore


#     def test_that_formatted_report_is_saved(self, testcase_report: TestCaseReport):
#         # given an initialized testcase report, a storage handler and naming conventions
#         report = testcase_report
#         formatter = DummyFormatter()
#         storage = DummyStorage()
#         naming_conventions = DummyNamingConventions()

#         # when report is formatted in a specified format
#         format = "my_format"
#         #_ = report.create_artifacts(format=format, formatter=formatter)

#         # and report is saved by testrun_id and start_ts
#         #report.save_artifacts(
#             location="any_location",
#             group_by=["testrun_id", "start_ts"],
#             storage=storage,
#             naming_conventions=naming_conventions,
#         )

#         # then it is written to specified location
#         written_locations = storage.written  # type: ignore
#         testrun_id = report.testrun_id
#         start_ts = report.start_ts
#         assert f"any_location/{testrun_id}/{start_ts}/report" in written_locations

#     def test_converting_testcase_report_to_dto(self, testcase_report):
#         # given a testcase report
#         testcase_report = testcase_report

#         # then converting report to dto results in a valid dto
#         assert isinstance(testcase_report.to_dto(), TestCaseReportDTO)


# class TestTestRunReport:
#     def test_creating_from_testrun_result(self, testcase_result):
#         # given a valid testrun result
#         testcase_results = [testcase_result, testcase_result]
#         testrun_result = TestRunResultDTO.from_testcase_results(
#             testcase_results=testcase_results
#         )

#         # when a testrun report is created from results
#         report = TestRunReport.from_testrun_result(testrun_result=testrun_result)

#         # then a valid report is created which contains all provided results
#         assert isinstance(report, TestRunReport)
#         assert report.testcase_results == testcase_results

#     def test_converting_to_dto(self, testrun_report):
#         # given a testrun report
#         report = testrun_report

#         # then conversion to dto results in valid testrun dto
#         assert isinstance(report.to_dto(), TestRunReportDTO)
#         assert report.testcase_results == report.to_dto().testcase_results
