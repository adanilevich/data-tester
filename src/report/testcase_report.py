from typing import Any, Dict, List, Self, Union

from src.report import AbstractReport
from src.dtos import TestCaseResultDTO, TestCaseReportDTO


class TestCaseReport(AbstractReport):
    def __init__(
        self,
        testcase_id: str,
        testrun_id: str,
        start_ts: str,
        end_ts: str,
        domain: str,
        stage: str,
        instance: str,
        testobject: str,
        testcase: str,
        result: str,
        summary: str,
        diff: Dict[str, Union[List, Dict]],
        facts: List[Dict[str, str | int]],
        details: List[Dict[str, Union[str, int, float]]],
        scenario: str = "",
        report_format: str | None = None,
        content_type: str | None = None,
        content: Any = None,
    ):
        self.testcase_id: str = testcase_id
        self.testrun_id: str = testrun_id
        self.start_ts: str = start_ts
        self.end_ts: str = end_ts
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
        self.report_format: str | None = report_format
        self.content_type: str | None = content_type
        self.content: Any = content

    @property
    def testcase_description(self):
        if self.testcase == "SCHEMA":
            desc = "Check that schema of testobject corresponds to specification."
            description = desc
        elif self.testcase == "ROWCOUNT":
            desc = "Check that rowcount in testobject mathces expectation."
            description = desc
        elif self.testcase == "COMPARE_SAMPLE":
            desc = "Full comparison of test SQL and tesobject on a data sample."
            description = desc
        else:
            description = "Testcase description is missing."

        return description

    def to_dto(self) -> TestCaseReportDTO:
        """"""
        return TestCaseReportDTO(
            testcase_id=self.testcase_id,
            testrun_id=self.testrun_id,
            start_ts=self.start_ts,
            end_ts=self.end_ts,
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
            report_format=self.report_format,
            content_type=self.content_type,
            content=self.content,
            description=self.description,
        )

    @classmethod
    def from_testcase_result(cls, testcase_result: TestCaseResultDTO) -> Self:
        return cls(
            testcase_id=testcase_result.testcase_id,
            testrun_id=testcase_result.testrun_id,
            start_ts=testcase_result.start_ts,
            end_ts=testcase_result.end_ts or "",
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
        )

    @classmethod
    def from_dto(
        cls,
        report_dto: TestCaseReportDTO,
    ) -> Self:
        return cls(
            testcase_id=report_dto.testcase_id,
            testrun_id=report_dto.testrun_id,
            start_ts=report_dto.start_ts,
            end_ts=report_dto.end_ts or "",
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
            report_format=report_dto.report_format,
            content_type=report_dto.content_type,
            content=report_dto.content,
        )
