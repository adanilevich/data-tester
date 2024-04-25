from typing import Any, Dict, List, Self, Union
from pydantic import model_validator, Field

from src.dtos import DTO, TestCaseResultDTO


class TestCaseReportDTO(DTO):

    testcase_id: str
    testrun_id: str
    start: str
    end: str
    domain: str
    stage: str
    instance: str
    testobject: str
    testcase: str
    scenario: str = ""
    description: str | None = None
    result: str
    summary: str
    diff:  Dict[str, Union[List, Dict]]
    facts: List[Dict[str, Any]]
    details: List[Dict[str, Any]]
    # format of content field, e.g. text, json, dict, xlsx
    format: str | None = Field(default=None)
    # content after formatting, can be string, bytes, other formats
    content: Any = Field(default=None)  # content of the formatted report

    @model_validator(mode="after")
    def set_description(self):
        if self.description is None or self.description == "":
            if self.testcase == "SCHEMA":
                desc = "Check that schema of testobject corresponds to specification."
                self.description = desc
            elif self.testcase == "ROWCOUNT":
                desc = "Check that rowcount in testobject mathces expectation."
                self.description = desc
            elif self.testcase == "COMPARE_SAMPLE":
                desc = "Full comparison of test SQL and tesobject on a data sample."
            else:
                raise ValueError(f"Testcase unknown: {self.testcase}")

    @classmethod
    def from_testcase_result(cls, testcase_result: TestCaseResultDTO) -> Self:
        raise NotImplementedError("constructing from testcase not yet implemented")


class ShortTestCaseResultDTO(DTO):

    domain: str
    stage: str
    instance: str
    testobject: str
    testcase: str
    scenario: str = ""
    result: str
    summary: str
    facts: str

    @classmethod
    def from_testcase_result(cls, testcase_result: TestCaseResultDTO) -> Self:
        raise NotImplementedError()


class TestRunReportDTO(DTO):

    testrun_id: str
    start: str
    end: str
    result: str
    testcase_results: List[ShortTestCaseResultDTO]
    format: str
    content: Any

    @classmethod
    def from_testcase_results(cls, testcase_results: List[TestCaseResultDTO]) -> Self:
        raise NotImplementedError
