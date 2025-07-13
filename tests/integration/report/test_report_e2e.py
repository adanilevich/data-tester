import random
import string
from typing import List
import json
import pytest

from src.report.dependency_injection import ReportDependencyInjector
from src.config import Config
from src.dtos import (
    DomainConfigDTO,
    TestCaseResultDTO,
    TestResult,
    TestType,
    TestRunResultDTO,
    TestCaseReportDTO,
)


@pytest.mark.skip(reason="Skipping report E2E tests")
class TestReportE2E:
    def test_report_e2e(
        self, domain_config: DomainConfigDTO, testcase_result: TestCaseResultDTO
    ):
        # given a configured report manager
        config = Config()
        config.DATATESTER_ENV = "LOCAL"
        domain_config.testreports_locations = ["dict://user_reports", "dict://user"]
        di = ReportDependencyInjector(config=config)
        report_manager = di.report_manager(domain_config=domain_config)

        # and a list of testcase results
        testcase_results: List[TestCaseResultDTO] = []
        for _ in range(10):
            # assign random testobject names, testtypes and results
            testobjects = [
                "".join(random.choices(string.ascii_letters, k=5)) for _ in range(100)
            ]
            testcase_result_ = testcase_result.copy()
            testcase_result_.result = random.choice(list(TestResult))
            testcase_result_.testobject.name = random.choice(testobjects)
            testcase_result_.testtype = random.choice(list(TestType))
            testcase_results.append(testcase_result_)

        # and given a corresponding testrun result
        testrun_result = TestRunResultDTO.from_testcase_results(testcase_results)

        # when creating and storing testcase and testrun reports
        testrun_report = report_manager.create_report(testrun_result)
        report_manager.save_report_artifacts_for_users(testrun_report)
        report_manager.save_report_in_internal_storage(testrun_report)

        testcase_reports: List[TestCaseReportDTO] = []  # noqa: F823
        for testcase_result in testrun_result.testcase_results:
            testcase_report = report_manager.create_report(testcase_result)
            report_manager.save_report_artifacts_for_users(testcase_report)
            report_manager.save_report_in_internal_storage(testcase_report)
            if not isinstance(testcase_report, TestCaseReportDTO):
                raise ValueError("Expected TestCaseReportDTO, got something else")
            testcase_reports.append(testcase_report)

        # then verify that reports were created and stored
        # Get access to storage instances for verification
        report_handler = report_manager.report_handler
        internal_storage = report_handler.storages[0]  # type: ignore

        # Verify internal storage contains all reports
        internal_location = str(config.INTERNAL_TESTREPORT_LOCATION)
        if not internal_location.endswith("/"):
            internal_location += "/"
        internal_format = config.INTERNAL_TESTREPORT_FORMAT.value.lower()

        # retrieve testrun report from internal storage
        testrun_internal_path = (
            f"{internal_location}{testrun_report.report_id}.{internal_format}"
        )
        testrun_internal_content = internal_storage.read(testrun_internal_path)
        testrun_internal_data = json.loads(testrun_internal_content.decode("utf-8"))

        # verify testrun report content
        assert testrun_internal_data["testrun_id"] == str(testrun_report.testrun_id)
        assert len(testrun_internal_data["testcase_results"]) == len(testcase_results)

        # Check each testcase report in internal storage
        for testcase_report in testcase_reports:
            testcase_internal_path = (
                f"{internal_location}{testcase_report.report_id}.{internal_format}"
            )
            content = internal_storage.read(testcase_internal_path)
            assert isinstance(content, bytes)

            # Verify testcase report content
            data = json.loads(content.decode("utf-8"))
            assert data["testcase_id"] == str(testcase_report.testcase_id)
            assert data["testrun_id"] == str(testcase_report.testrun_id)
            assert data["testobject"] == testcase_report.testobject
            assert data["testtype"] == testcase_report.testtype

        # Verify user storage contains artifacts
        user_locations = domain_config.testreports_locations
        date_str = testrun_report.start_ts.strftime("%Y-%m-%d")
        datetime_str = testrun_report.start_ts.strftime("%Y-%m-%d_%H-%M-%S")

        user_storage = report_handler.storages[1]  # type: ignore
        for user_location in user_locations:
            # Check testrun artifact in user storage
            testrun_user_path = (
                f"{user_location}/{date_str}/{testrun_report.testrun_id}/"
                f"testrun_report_{datetime_str}."
                f"{config.TESTRUN_REPORT_ARTIFACT_FORMAT.value.lower()}"
            )
            content = user_storage.read(testrun_user_path)
            assert isinstance(content, bytes)

            # Verify XLSX format for testrun report
            if config.TESTRUN_REPORT_ARTIFACT_FORMAT.value.lower() == "xlsx":
                assert content.startswith(b"PK\x03\x04")  # XLSX format

            # Check testcase artifacts in user storage
            for testcase_report in testcase_reports:
                # Check testcase report artifact
                testcase_user_path = (
                    f"{user_location}/{date_str}/{testcase_report.testrun_id}/"
                    f"{testcase_report.testobject}_{testcase_report.testtype}_report."
                    f"{config.TESTCASE_REPORT_ARTIFACT_FORMAT.value.lower()}"
                )
                content = user_storage.read(testcase_user_path)
                assert isinstance(content, bytes)

                # Verify TXT format for testcase report
                if config.TESTCASE_REPORT_ARTIFACT_FORMAT.value.lower() == "txt":
                    testcase_text = content.decode("utf-8")
                    assert testcase_report.summary in testcase_text
                    assert testcase_report.testobject in testcase_text
                    assert testcase_report.testtype in testcase_text

                # Check diff artifact if testcase has diff data
                if testcase_report.diff and len(testcase_report.diff) > 0:
                    testcase_diff_path = (
                        f"{user_location}/{date_str}/{testcase_report.testrun_id}/"
                        f"{testcase_report.testobject}_{testcase_report.testtype}_diff."
                        f"{config.TESTCASE_DIFF_ARTIFACT_FORMAT.value.lower()}"
                    )
                    content = user_storage.read(testcase_diff_path)
                    assert isinstance(content, bytes)

                    # Verify XLSX format for diff
                    if config.TESTCASE_DIFF_ARTIFACT_FORMAT.value.lower() == "xlsx":
                        assert content.startswith(b"PK\x03\x04")  # XLSX format
