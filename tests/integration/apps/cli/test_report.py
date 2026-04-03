import random
import string
from typing import List, Tuple

import pytest

from src.apps.cli_di import CliDependencyInjector
from src.drivers import ReportDriver
from src.config import Config
from src.dtos import (
    TestCaseDTO,
    TestResult,
    TestType,
    TestRunDTO,
    TestCaseReportDTO,
    TestRunReportDTO,
)
from src.domain_ports import (
    LoadTestCaseReportCommand,
    LoadTestRunReportCommand,
)


@pytest.fixture
def report_manager(testcase_result: TestCaseDTO) -> ReportDriver:
    config = Config()
    config.DATATESTER_ENV = "LOCAL"
    di = CliDependencyInjector(config=config)
    return di.report_driver()


@pytest.fixture
def testresults(
    testcase_result: TestCaseDTO,
) -> Tuple[TestRunDTO, List[TestCaseDTO]]:
    testcase_results: List[TestCaseDTO] = []
    for _ in range(10):
        testobjects = [
            "".join(random.choices(string.ascii_letters, k=5)) for _ in range(100)
        ]
        testcase_result_ = testcase_result.copy()
        testcase_result_.result = random.choice(list(TestResult))
        testcase_result_.testobject.name = random.choice(testobjects)
        testcase_result_.testtype = random.choice(list(TestType))
        testcase_results.append(testcase_result_)

    testrun_result = TestRunDTO.from_testcases(testcases=testcase_results)

    return testrun_result, testcase_results


def create_and_save_reports(
    report_manager: ReportDriver,
    testresults: Tuple[TestRunDTO, List[TestCaseDTO]],
) -> Tuple[TestRunReportDTO, List[TestCaseReportDTO]]:
    testrun_result, testcase_results = testresults

    testrun_report = report_manager.create_testrun_report(testrun_result)
    report_manager.save_report(testrun_report)

    testcase_reports: List[TestCaseReportDTO] = []
    for testcase_result in testrun_result.testcase_results:
        testcase_report = report_manager.create_testcase_report(testcase_result)
        report_manager.save_report(testcase_report)
        testcase_reports.append(testcase_report)

    return testrun_report, testcase_reports


class TestReportE2E:
    def test_create_and_save_reports(
        self,
        report_manager: ReportDriver,
        testresults: Tuple[TestRunDTO, List[TestCaseDTO]],
    ):
        testrun_result, testcase_results = testresults

        testrun_report, testcase_reports = create_and_save_reports(
            report_manager, testresults
        )

        assert isinstance(testrun_report, TestRunReportDTO)
        assert isinstance(testcase_reports, list)
        assert all(isinstance(report, TestCaseReportDTO) for report in testcase_reports)
        assert len(testrun_report.testcase_results) == len(testcase_results)

    def test_retrieve_from_internal_storage(
        self,
        report_manager: ReportDriver,
        testresults: Tuple[TestRunDTO, List[TestCaseDTO]],
    ):
        report_handler = report_manager.report_handler

        testrun_report, testcase_reports = create_and_save_reports(
            report_manager, testresults
        )

        # retrieve testrun report
        report_dto = report_handler.load_testrun_report(
            command=LoadTestRunReportCommand(
                report_id=testrun_report.report_id,
            )
        )

        assert str(report_dto.testrun_id) == str(testrun_report.testrun_id)
        assert len(report_dto.testcase_results) == len(testcase_reports)

        # retrieve testcase reports
        for testcase_report in testcase_reports:
            tc_report_dto = report_handler.load_testcase_report(
                command=LoadTestCaseReportCommand(
                    report_id=testcase_report.report_id,
                )
            )
            assert str(tc_report_dto.testcase_id) == str(testcase_report.testcase_id)
            assert str(tc_report_dto.testrun_id) == str(testcase_report.testrun_id)
            assert tc_report_dto.testobject == testcase_report.testobject
            assert tc_report_dto.testtype == testcase_report.testtype

    def test_create_and_save_all_reports(
        self,
        report_manager: ReportDriver,
        testresults: Tuple[TestRunDTO, List[TestCaseDTO]],
    ):
        testrun_result, _ = testresults

        result = report_manager.create_and_save_all_reports(testrun_result)

        assert isinstance(result, TestRunReportDTO)
        assert testrun_result.report_id == result.report_id
        for tc in testrun_result.testcase_results:
            assert tc.report_id is not None
