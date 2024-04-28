from typing import Any, Dict, List, Self, Union

from src.report.ports import IStorage, IReportFormatter, IReportNamingConventions
from src.report import AbstractReport
from src.dtos import TestCaseResultDTO, TestCaseReportDTO


class TestCaseReport(AbstractReport):

    @classmethod
    def from_testcase_result(
        cls,
        testcase_result: TestCaseResultDTO,
        formatter: IReportFormatter,
        storage: IStorage,
        naming_conventions: IReportNamingConventions,
    ) -> Self:
        """"""
        return cls(
            testcase_id=testcase_result.id,
            testrun_id=testcase_result.run_id,
            start=testcase_result.start_ts,
            end=testcase_result.end_ts or "",
            domain=testcase_result.testobject.domain,
            stage=testcase_result.testobject.stage,
            instance=testcase_result.testobject.instance,
            testobject=testcase_result.testobject.name,
            testcase=testcase_result.testtype,
            result=testcase_result.result.value,
            summary=testcase_result.summary,
            diff=testcase_result.diff,
            facts=testcase_result.facts,
            details=testcase_result.details,
            scenario=testcase_result.scenario,
            formatter=formatter,
            storage=storage,
            naming_conventions=naming_conventions,
        )

    @classmethod
    def from_dto(
        cls,
        report_dto: TestCaseReportDTO,
        formatter: IReportFormatter,
        storage: IStorage,
        naming_conventions: IReportNamingConventions,
    ):
        return cls(
            testcase_id=report_dto.testcase_id,
            testrun_id=report_dto.testrun_id,
            start=report_dto.start,
            end=report_dto.end or "",
            domain=report_dto.domain,
            stage=report_dto.stage,
            instance=report_dto.instance,
            testobject=report_dto.testobject,
            testcase=report_dto.testcase,
            result=report_dto.result,
            summary=report_dto.summary,
            diff=report_dto.diff,
            facts=report_dto.facts,
            details=report_dto.details,
            scenario=report_dto.scenario,
            format=report_dto.format,
            content_type=report_dto.content_type,
            content=report_dto.content,
            formatter=formatter,
            storage=storage,
            naming_conventions=naming_conventions,
        )

    def __init__(self, formatter: IReportFormatter, storage: IStorage,
                 naming_conventions: IReportNamingConventions, testcase_id: str,
                 testrun_id: str, start: str, end: str, domain: str, stage: str,
                 instance: str, testobject: str, testcase: str, result: str,
                 summary: str, diff:  Dict[str, Union[List, Dict]],
                 facts: List[Dict[str, str | int]],
                 details: List[Dict[str, Union[str, int, float]]],
                 scenario: str = "", format: str | None = None,
                 content_type: str | None = None, content: Any = None):

        self.testcase_id: str = testcase_id
        self.testrun_id: str = testrun_id
        self.start: str = start
        self.end: str = end
        self.domain: str = domain
        self.stage: str = stage
        self.instance: str = instance
        self.testobject: str = testobject
        self.testcase: str = testcase
        self.scenario: str = scenario
        self.result: str = result
        self.summary: str = summary
        self.diff: Dict[str, Union[List, Dict]] = diff
        self.facts: List[Dict[str, str | int]] = facts
        self.details: List[Dict[str, Union[str, int, float]]] = details
        self.description: str = self.testcase_description
        self.format: str | None = format
        self.content_type: str | None = content_type
        self.content: Any = content
        self.formatter: IReportFormatter = formatter
        self.storage: IStorage = storage
        self.naming_conventions: IReportNamingConventions = naming_conventions

    @property
    def testcase_description(self):
        if self.description is None or self.description == "":
            if self.testcase == "SCHEMA":
                desc = "Check that schema of testobject corresponds to specification."
                self.description = desc
            elif self.testcase == "ROWCOUNT":
                desc = "Check that rowcount in testobject mathces expectation."
                self.description = desc
            elif self.testcase == "COMPARE_SAMPLE":
                desc = "Full comparison of test SQL and tesobject on a data sample."
                self.description = desc
            else:
                self.description = "Testcase description is missing."

    def to_dto(self) -> TestCaseReportDTO:
        """"""
        return TestCaseReportDTO(
            testcase_id=self.testcase_id,
            testrun_id=self.testrun_id,
            start=self.start,
            end=self.end,
            domain=self.domain,
            stage=self.stage,
            instance=self.instance,
            testobject=self.testobject,
            testcase=self.testcase,
            result=self.result,
            summary=self.summary,
            diff=self.diff,
            facts=self.facts,
            details=self.details,
            scenario=self.scenario,
            format=self.format,
            content_type=self.content_type,
            content=self.content,
        )
