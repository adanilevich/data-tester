import random
import string
from typing import List, Tuple, cast

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
    ReportType,
)
from src.domain_ports import LoadReportCommand


@pytest.fixture
def report_manager(
    testcase_result: TestCaseDTO,
) -> ReportDriver:
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
            "".join(
                random.choices(string.ascii_letters, k=5)
            )
            for _ in range(100)
        ]
        testcase_result_ = testcase_result.copy()
        testcase_result_.result = random.choice(
            list(TestResult)
        )
        testcase_result_.testobject.name = random.choice(
            testobjects
        )
        testcase_result_.testtype = random.choice(
            list(TestType)
        )
        testcase_results.append(testcase_result_)

    testrun_result = TestRunDTO.from_testcases(
        testcases=testcase_results
    )

    return testrun_result, testcase_results


def create_and_save_reports(
    report_manager: ReportDriver,
    testresults: Tuple[TestRunDTO, List[TestCaseDTO]],
) -> Tuple[TestRunReportDTO, List[TestCaseReportDTO]]:
    testrun_result, testcase_results = testresults

    testrun_report: TestRunReportDTO
    testrun_report = report_manager.create_report(testrun_result)  # type: ignore
    report_manager.save_report(testrun_report)

    testcase_reports: List[TestCaseReportDTO] = []
    for testcase_result in testrun_result.testcase_results:
        testcase_report = report_manager.create_report(
            testcase_result
        )
        report_manager.save_report(testcase_report)
        testcase_reports.append(testcase_report)  # type: ignore

    return testrun_report, testcase_reports


class TestReportE2E:
    def test_create_and_save_reports(
        self,
        report_manager: ReportDriver,
        testresults: Tuple[TestRunDTO, List[TestCaseDTO]],
    ):
        testrun_result, testcase_results = testresults

        testrun_report, testcase_reports = (
            create_and_save_reports(
                report_manager, testresults
            )
        )

        assert isinstance(testrun_report, TestRunReportDTO)
        assert isinstance(testcase_reports, list)
        assert all(
            isinstance(report, TestCaseReportDTO)
            for report in testcase_reports
        )
        assert len(testrun_report.testcase_results) == len(
            testcase_results
        )

    def test_retrieve_from_internal_storage(
        self,
        report_manager: ReportDriver,
        testresults: Tuple[TestRunDTO, List[TestCaseDTO]],
    ):
        report_handler = report_manager.report_handler
        testrun_result, testcase_results = testresults

        testrun_report, testcase_reports = (
            create_and_save_reports(
                report_manager, testresults
            )
        )

        # retrieve testrun report
        report_dto = report_handler.load_report(
            command=LoadReportCommand(
                report_id=testrun_report.report_id,
                report_type=ReportType.TESTRUN,
            )
        )
        report_dto = cast(TestRunReportDTO, report_dto)

        assert str(report_dto.testrun_id) == str(
            testrun_report.testrun_id
        )
        assert len(report_dto.testcase_results) == len(
            testcase_reports
        )

        # retrieve testcase reports
        for testcase_report in testcase_reports:
            report_dto = report_handler.load_report(
                command=LoadReportCommand(
                    report_id=testcase_report.report_id,
                    report_type=ReportType.TESTCASE,
                )
            )
            report_dto = cast(TestCaseReportDTO, report_dto)
            assert str(report_dto.testcase_id) == str(
                testcase_report.testcase_id
            )
            assert str(report_dto.testrun_id) == str(
                testcase_report.testrun_id
            )
            assert (
                report_dto.testobject
                == testcase_report.testobject
            )
            assert (
                report_dto.testtype
                == testcase_report.testtype
            )
