from __future__ import annotations
from enum import Enum
from typing import Dict, Union, List, Self
from datetime import datetime
from uuid import uuid4

from pydantic import UUID4

from src.dtos.dto import DTO
from src.dtos.specification import SpecificationDTO
from src.dtos.testcase import TestCaseDTO
from src.dtos.testcase import TestRunDTO


class ReportArtifactFormat(Enum):
    JSON = "json"
    TXT = "txt"
    XLSX = "xlsx"


class ReportArtifact(Enum):
    REPORT = "report"
    DIFF = "diff"


class ReportType(Enum):
    TESTCASE = "testcase"
    TESTRUN = "testrun"


class TestReportDTO(DTO):
    __test__ = False  # prevents pytest collection
    report_id: UUID4
    testrun_id: UUID4
    testset_id: UUID4
    labels: List[str]
    result: str
    start_ts: datetime
    end_ts: datetime


class TestCaseReportDTO(TestReportDTO):
    __test__ = False  # prevents pytest collection
    testcase_id: UUID4
    testobject: str
    testtype: str
    diff: Dict[str, Union[List, Dict]]  # diff as a table in record-oriented dict
    summary: str
    facts: List[Dict[str, str | int]]
    details: List[Dict[str, Union[str, int, float]]]
    specifications: List[SpecificationDTO]

    @property
    def object_id(self) -> str:
        """Object ID for storage purposes."""
        return str(self.report_id)

    @classmethod
    def from_testcase_result(cls, testcase_result: TestCaseDTO) -> Self:
        return cls(
            report_id=uuid4(),
            testrun_id=testcase_result.testrun_id,
            testset_id=testcase_result.testset_id,
            labels=testcase_result.labels,
            result=testcase_result.result.value,
            start_ts=testcase_result.start_ts,
            end_ts=testcase_result.end_ts or datetime.now(),
            testcase_id=testcase_result.testcase_id,
            testobject=testcase_result.testobject.name,
            testtype=testcase_result.testtype.value,
            diff=testcase_result.diff,
            summary=testcase_result.summary,
            facts=testcase_result.facts,
            details=testcase_result.details,
            specifications=testcase_result.specifications,
        )


class TestRunReportTestCaseEntryDTO(TestReportDTO):
    __test__ = False  # prevents pytest collection
    testobject: str
    testtype: str
    summary: str

    @classmethod
    def from_testcase_result(cls, testcase_result: TestCaseDTO) -> Self:
        return cls(
            report_id=uuid4(),
            testrun_id=testcase_result.testrun_id,
            testset_id=testcase_result.testset_id,
            labels=testcase_result.labels,
            result=testcase_result.result.value,
            start_ts=testcase_result.start_ts,
            end_ts=testcase_result.end_ts or datetime.now(),
            testobject=testcase_result.testobject.name,
            testtype=testcase_result.testtype.value,
            summary=testcase_result.summary,
        )


class TestRunReportDTO(TestReportDTO):
    __test__ = False  # prevents pytest collection
    testcase_results: List[TestRunReportTestCaseEntryDTO]

    @property
    def object_id(self) -> str:
        """Object ID for storage purposes."""
        return str(self.report_id)

    @classmethod
    def from_testrun(cls, testrun: TestRunDTO) -> Self:
        return cls(
            report_id=uuid4(),
            testrun_id=testrun.testrun_id,
            testset_id=testrun.testset_id,
            labels=testrun.labels,
            result=testrun.result.value,
            start_ts=testrun.start_ts,
            end_ts=testrun.end_ts or datetime.now(),
            testcase_results=[
                TestRunReportTestCaseEntryDTO.from_testcase_result(testcase_result)
                for testcase_result in testrun.testcase_results
            ],
        )
