# import pytest
# import polars as pl
# from io import BytesIO
# from src.report.adapters import SimpleReportFormatter
# from src.dtos import TestCaseReportDTO, TestRunReportDTO


# class TestSimpleReportFormatter:
#     def test_that_unknown_format_raises_error(self, testcase_report):
#         # given a testcase report and a formatter
#         report = testcase_report
#         formatter = SimpleReportFormatter()

#         # when an unknown format is requested
#         format = "any_value"

#         # then trying to format the report fails
#         with pytest.raises(ValueError):
#             _ = formatter.format(report=report, format=format)

#     def test_that_xlsx_formatting_only_works_for_testrun_reports(
#         self,
#         testcase_report: TestCaseReportDTO,
#     ):
#         # given a testcase report and a formatter
#         report = testcase_report
#         formatter = SimpleReportFormatter()

#         # when an unknown format is requested
#         format = "xlsx"

#         # then trying to format the report fails
#         with pytest.raises(ValueError):
#             _ = formatter.format(report=report, format=format)

#     def test_that_txt_formatting_only_works_for_testcase_reports(
#         self,
#         testrun_report: TestRunReportDTO,
#     ):
#         # given a testrun report and a formatter
#         report = testrun_report
#         formatter = SimpleReportFormatter()

#         # when an unknown format is requested
#         format = "txt"

#         # then trying to format the report fails
#         with pytest.raises(ValueError):
#             _ = formatter.format(report=report, format=format)

#     def test_xlsx_formatting_for_testrun_report(self, testrun_report: TestRunReportDTO):
#         # given a testrun report and a formatter
#         report = testrun_report
#         formatter = SimpleReportFormatter()

#         # when an unknown format is requested
#         format = "xlsx"

#         # then report is correctly formatted
#         format, content_type, content = formatter.format(report=report, format=format)
#         df = pl.read_excel(BytesIO(content))
#         for col in ["testrun_id", "start_ts", "end_ts", "result"]:
#             assert col in df.columns
#         assert format == "xlsx"
#         assert "template" in content_type
#         assert df.shape[0] == 2

#     def test_dict_formatting(self, testcase_report, testrun_report):
#         # given a testrun report and a testcase_report
#         testcase_report = testcase_report
#         testrun_report = testrun_report
#         formatter = SimpleReportFormatter()

#         # when an unknown format is requested
#         format = "dict"

#         # then report is correctly formatted
#         format, content_type, content = formatter.format(
#             report=testrun_report, format=format
#         )
#         assert TestRunReportDTO.from_dict(content)
#         assert format == "dict"
#         assert content_type == "application/json"

#         format, content_type, content = formatter.format(
#             report=testcase_report, format=format
#         )
#         assert TestCaseReportDTO.from_dict(content)
#         assert format == "dict"
#         assert content_type == "application/json"
