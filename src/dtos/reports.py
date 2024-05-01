from typing import Any, Dict, List, Union
from pydantic import Field

from src.dtos import DTO, TestCaseResultDTO


class TestCaseReportDTO(DTO):
    testcase_id: str
    testrun_id: str
    start_ts: str
    end_ts: str
    domain: str
    stage: str
    instance: str
    testobject: str
    testcase: str
    scenario: str = ""
    description: str | None = None
    result: str
    summary: str
    diff: Dict[str, Union[List, Dict]]
    facts: List[Dict[str, str | int]]
    details: List[Dict[str, Any]]
    # Format of testcase report in business terms, e.g. 'xlsx' or 'text'
    report_format: str | None = Field(default=None)
    # Content/Mime type of report, e.g.
    #   for excel 'application/vnd.opnexmlformats-officedocument.spreadsheetml.tmeplate'
    #   for text file 'text/plain'
    content_type: str | None = Field(default=None)
    # content of the report - string content or dict or excel as bytes, etc.
    content: Any = Field(default=None)


class TestRunReportDTO(DTO):
    testrun_id: str
    start_ts: str
    end_ts: str
    result: str
    testcase_results: List[TestCaseResultDTO]
    # Format of testcase report in business terms, e.g. 'xlsx' or 'text'
    report_format: str | None = Field(default=None)
    # Content/Mime type of report, e.g.
    #   for excel 'application/vnd.opnexmlformats-officedocument.spreadsheetml.tmeplate'
    #   for text file 'text/plain'
    content_type: str | None = Field(default=None)
    # content of the report - string content or dict or excel as bytes, etc.
    content: Any = Field(default=None)
