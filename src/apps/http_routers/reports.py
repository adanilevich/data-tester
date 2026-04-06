from typing import List
from uuid import UUID

from fastapi import APIRouter

from src.apps.http_di import ReportDriverDep
from src.dtos.report_dtos import TestCaseReportDTO, TestRunReportDTO

router = APIRouter(tags=["reports"])


@router.get("/{domain}/testcase-report/", response_model=List[TestCaseReportDTO])
def list_testcase_reports(
    domain: str,
    driver: ReportDriverDep,
    testrun_id: UUID | None = None,
    date: str | None = None,
) -> List[TestCaseReportDTO]:
    return driver.list_testcase_reports(domain=domain, testrun_id=testrun_id, date=date)


@router.get("/{domain}/testcase-report/{report_id}", response_model=TestCaseReportDTO)
def load_testcase_report(
    domain: str, report_id: UUID, driver: ReportDriverDep
) -> TestCaseReportDTO:
    return driver.load_testcase_report(report_id=report_id)


@router.get("/{domain}/testrun-report/", response_model=List[TestRunReportDTO])
def list_testrun_reports(
    domain: str,
    driver: ReportDriverDep,
    date: str | None = None,
) -> List[TestRunReportDTO]:
    return driver.list_testrun_reports(domain=domain, date=date)


@router.get("/{domain}/testrun-report/{report_id}", response_model=TestRunReportDTO)
def load_testrun_report(
    domain: str, report_id: UUID, driver: ReportDriverDep
) -> TestRunReportDTO:
    return driver.load_testrun_report(report_id=report_id)
