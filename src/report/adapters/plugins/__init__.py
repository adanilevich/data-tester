# ruff: noqa
from src.report.adapters.plugins.txt_testcase_report import TxtTestCaseReportFormatter
from src.report.adapters.plugins.xlsx_testcase_diff import XlsxTestCaseDiffFormatter
from src.report.adapters.plugins.xlsx_testrun_report import XlsxTestRunReportFormatter
from src.report.adapters.plugins.json_report import (
    JsonTestCaseReportFormatter,
    JsonTestRunReportFormatter,
)