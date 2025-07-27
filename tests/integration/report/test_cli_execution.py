import random
import string
from typing import List, Tuple, cast

import pytest

from src.report.drivers import CliReportManager
from src.report.dependency_injection import ReportDependencyInjector
from src.config import Config
from src.dtos import (
    DomainConfigDTO,
    TestCaseDTO,
    TestResult,
    TestType,
    TestRunDTO,
    TestCaseReportDTO,
    LocationDTO,
    TestRunReportDTO,
    ReportType,
)
from src.report.ports import LoadReportCommand


@pytest.fixture
def report_manager(
    domain_config: DomainConfigDTO,
    testcase_result: TestCaseDTO
) -> CliReportManager:
    config = Config()
    config.DATATESTER_ENV = "LOCAL"
    domain_config.testreports_location = LocationDTO("dict://user_reports")
    di = ReportDependencyInjector(config=config)
    return di.cli_report_manager(domain_config=domain_config)

@pytest.fixture
def testresults(
    testcase_result: TestCaseDTO
) -> Tuple[TestRunDTO, List[TestCaseDTO]]:
        # create 10 random testcase results
        testcase_results: List[TestCaseDTO] = []
        for _ in range(10):
            # assign random testobject names, testtyp   es and results
            testobjects = [
                "".join(random.choices(string.ascii_letters, k=5)) for _ in range(100)
            ]
            testcase_result_ = testcase_result.copy()
            testcase_result_.result = random.choice(list(TestResult))
            testcase_result_.testobject.name = random.choice(testobjects)
            testcase_result_.testtype = random.choice(list(TestType))
            testcase_results.append(testcase_result_)

        # create a corresponding testrun result
        testrun_result = TestRunDTO.from_testcases(testcases=testcase_results)

        return testrun_result, testcase_results

def create_and_save_reports(
    report_manager: CliReportManager,
    testresults: Tuple[TestRunDTO, List[TestCaseDTO]]
) -> Tuple[TestRunReportDTO, List[TestCaseReportDTO]]:

    testrun_result, testcase_results = testresults

    testrun_report: TestRunReportDTO
    testrun_report = report_manager.create_report(testrun_result) # type: ignore
    report_manager.save_report_artifacts_for_users(testrun_report)
    report_manager.save_report_in_internal_storage(testrun_report)

    testcase_reports: List[TestCaseReportDTO] = []
    for testcase_result in testrun_result.testcase_results:
        testcase_report = report_manager.create_report(testcase_result)
        report_manager.save_report_artifacts_for_users(testcase_report)
        report_manager.save_report_in_internal_storage(testcase_report)
        testcase_reports.append(testcase_report)  # type: ignore

    return testrun_report, testcase_reports

class TestReportE2E:

    def test_create_and_save_reports(
        self,
        report_manager: CliReportManager,
        testresults: Tuple[TestRunDTO, List[TestCaseDTO]]
    ):
        # given a configured report manager and testresults
        report_manager = report_manager
        testrun_result, testcase_results = testresults

        # when reports are created and saved
        testrun_report, testcase_reports = create_and_save_reports(
            report_manager, testresults)

        # then created reports are of correct type
        assert isinstance(testrun_report, TestRunReportDTO)
        assert isinstance(testcase_reports, list)
        assert all(isinstance(report, TestCaseReportDTO) for report in testcase_reports)

        # and the testrun report contains the correct number of testcase results
        assert len(testrun_report.testcase_results) == len(testcase_results)

    def test_retrieve_from_internal_storage(
        self,
        report_manager: CliReportManager,
        testresults: Tuple[TestRunDTO, List[TestCaseDTO]]
    ):
        # given a configured report manager and testresults
        report_manager = report_manager
        report_handler = report_manager.report_handler
        testrun_result, testcase_results = testresults

        # when reports are created and saved
        testrun_report, testcase_reports = create_and_save_reports(
            report_manager, testresults)

        # then the testrun report can be retrieved from internal storage
        internal_location = report_manager.internal_location
        report_dto = report_handler.load_report(
            command=LoadReportCommand(
                location=internal_location,
                report_id=testrun_report.report_id,
                report_type=ReportType.TESTRUN,
            )
        )
        report_dto = cast(TestRunReportDTO, report_dto)

        # and the testrun report content is correct
        assert str(report_dto.testrun_id) == str(testrun_report.testrun_id)
        assert len(report_dto.testcase_results) == len(testcase_reports)

        # and the testcase reports can be retrieved from internal storage
        for testcase_report in testcase_reports:
            report_dto = report_handler.load_report(
                command=LoadReportCommand(
                    location=internal_location,
                    report_id=testcase_report.report_id,
                    report_type=ReportType.TESTCASE,
                )
            )
            report_dto = cast(TestCaseReportDTO, report_dto)
            # verify testcase report content
            assert str(report_dto.testcase_id) == str(testcase_report.testcase_id)
            assert str(report_dto.testrun_id) == str(testcase_report.testrun_id)
            assert report_dto.testobject == testcase_report.testobject
            assert report_dto.testtype == testcase_report.testtype


    def test_retrieve_from_user_storage(
        self,
        report_manager: CliReportManager,
        testresults: Tuple[TestRunDTO, List[TestCaseDTO]]
    ):

        # given a configured report manager and testresults
        report_manager = report_manager
        testrun_result, testcase_results = testresults
        handler = report_manager.report_handler

        user_location = report_manager.user_location
        user_storage = handler.storage_factory.get_storage(  # type: ignore
            user_location)

        # when reports are created and saved
        testrun_report, testcase_reports = create_and_save_reports(
            report_manager, testresults)

        # then the testrun report can be retrieved from user storage
        date_str = testrun_report.start_ts.strftime("%Y-%m-%d")
        datetime_str = testrun_report.start_ts.strftime("%Y-%m-%d_%H-%M-%S")

        testrun_user_path = user_location.append(
            f"{date_str}/{testrun_report.testrun_id}/"
            f"testrun_report_{datetime_str}."
            f"{report_manager.user_testrun_format.value.lower()}"
        )
        content = user_storage.read_bytes(testrun_user_path)
        assert isinstance(content, bytes)

        # and the testrun report content is a valid XLSX file
        assert content.startswith(b"PK\x03\x04")

        # and the testcase reports can be retrieved from user storage
        for testcase_report in testcase_reports:
            testcase_user_path = user_location.append(
                f"{date_str}/{testcase_report.testrun_id}/"
                f"{testcase_report.testobject}_{testcase_report.testtype}_report."
                f"{report_manager.user_report_format.value.lower()}"
            )
            content = user_storage.read_bytes(testcase_user_path)
            assert isinstance(content, bytes)

            # and the testcase report content is a valid TXT file
            testcase_text = content.decode("utf-8")
            assert testcase_report.summary in testcase_text
            assert testcase_report.testobject in testcase_text
            assert testcase_report.testtype in testcase_text

            # if there is no diff, skip
            if not (testcase_report.diff or len(testcase_report.diff) > 0):
                continue

            # if there is a diff, the diff artifact can be retrieved from user storage
            testcase_diff_path = user_location.append(
                f"{date_str}/{testcase_report.testrun_id}/"
                f"{testcase_report.testobject}_{testcase_report.testtype}_diff."
                f"{report_manager.user_diff_format.value.lower()}"
            )
            content = user_storage.read_bytes(testcase_diff_path)
            assert isinstance(content, bytes)

            # and the diff artifact content is a valid XLSX file
            assert content.startswith(b"PK\x03\x04")
