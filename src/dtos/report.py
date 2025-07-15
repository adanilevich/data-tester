from __future__ import annotations
from enum import Enum
from typing import Dict, Union, List, Self
from datetime import datetime
from uuid import uuid4

from pydantic import UUID4

from src.dtos import DTO, SpecificationDTO, TestCaseResultDTO, TestRunResultDTO


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

    @classmethod
    def from_testcase_result(cls, testcase_result: TestCaseResultDTO) -> Self:
        return cls(
            report_id = uuid4(),
            testrun_id=testcase_result.testrun_id,
            testset_id=testcase_result.testset_id,
            labels=testcase_result.labels,
            result=testcase_result.result.value,
            start_ts=testcase_result.start_ts,
            end_ts=testcase_result.end_ts,
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
    def from_testcase_result(cls, testcase_result: TestCaseResultDTO) -> Self:
        return cls(
            report_id = uuid4(),
            testrun_id=testcase_result.testrun_id,
            testset_id=testcase_result.testset_id,
            labels=testcase_result.labels,
            result=testcase_result.result.value,
            start_ts=testcase_result.start_ts,
            end_ts=testcase_result.end_ts,
            testobject=testcase_result.testobject.name,
            testtype=testcase_result.testtype.value,
            summary=testcase_result.summary,
        )


class TestRunReportDTO(TestReportDTO):
    __test__ = False  # prevents pytest collection
    testcase_results: List[TestRunReportTestCaseEntryDTO]

    @classmethod
    def from_testrun_result(cls, testrun_result: TestRunResultDTO) -> Self:
        return cls(
            report_id = uuid4(),
            testrun_id=testrun_result.testrun_id,
            testset_id=testrun_result.testset_id,
            labels=testrun_result.labels,
            result=testrun_result.result.value,
            start_ts=testrun_result.start_ts,
            end_ts=testrun_result.end_ts,
            testcase_results=[
                TestRunReportTestCaseEntryDTO.from_testcase_result(testcase_result)
                for testcase_result in testrun_result.testcase_results
            ],
        )
