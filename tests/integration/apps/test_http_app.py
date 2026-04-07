"""
Integration tests for the FastAPI HTTP backend — payments domain only.

Tests the full pipeline against the demo backend, using the session-scoped
demo_data fixture. The sales domain is tested separately in test_cli_app.py.
"""

from src.client_interface.requests import ExecuteTestRunRequest, FindSpecsRequest

from datetime import datetime

import pytest
from fastapi.testclient import TestClient

from src.dtos.specification_dtos import SpecDTO
from tests.conftest import DemoData
from src.apps.http_app import create_app
from src.config import Config
from src.dtos import (
    DomainConfigDTO,
    TestCaseReportDTO,
    TestRunDTO,
    TestRunReportDTO,
    TestSetDTO,
    TestCaseEntryDTO,
    TestType,
)


@pytest.fixture(scope="module")
def client(demo_data: DemoData):
    """Test Client for demo data and backend"""
    config = Config(
        DATATESTER_DATA_PLATFORM="DEMO",
        DATATESTER_USER_STORAGE_ENGINE="LOCAL",
        DATATESTER_INTERNAL_STORAGE_LOCATION=demo_data.internal_location,
        DATATESTER_DEMO_RAW_PATH=demo_data.raw_path,
        DATATESTER_DEMO_DB_PATH=demo_data.db_path,
    )
    app = create_app(config)
    with TestClient(app) as client:
        client.timeout = None
        yield client


def _assert_testcase_results(
    results: list[tuple[str, str, str]], expected: list[tuple[str, str, str]]
) -> None:
    """Assert actual results match expected (testobject, testtype, result).

    Sorts both lists before comparing so order doesn't matter.
    """
    assert len(results) == len(expected), (
        f"Expected {len(expected)} results, got {len(results)}"
    )
    assert sorted(results) == sorted(expected)


class TestFullFlowPayments:
    """Full flow: domain config -> testset -> specs -> testrun -> reports.

    Payments domain has 7 testcases (6 original + 1 duplicate added in test).
    All OK except stage_transactions STAGECOUNT which is NOK
    (transactions_2 truncated during staging).
    """

    # Expected results: (testobject, testtype, result) — includes the duplicate
    EXPECTED_RESULTS: list[tuple[str, str, str]] = [
        ("stage_accounts", "SCHEMA", "OK"),
        ("stage_accounts", "SCHEMA", "OK"),
        # this is not in testset which is persisted via fixture, but
        # added during the test flow execution:
        ("stage_transactions", "SCHEMA", "OK"),
        ("core_account_payments", "ROWCOUNT", "OK"),
        ("core_account_payments", "COMPARE", "OK"),
        ("stage_accounts", "STAGECOUNT", "OK"),
        ("stage_transactions", "STAGECOUNT", "NOK"),
    ]

    def test_full_flow(self, client: TestClient):
        ### response.content is ALWAYS bytes (i.e. a json)
        ### response.json is ALWAYS a dict
        ### put ALWAYS expects a json-serialiable dict, i.e. dto.to_dict()
        # 1. Load domain config, modify, persist, reload and validate
        dc_get = client.get("/domain-config/payments")
        assert dc_get.status_code == 200
        dc_dto = DomainConfigDTO.from_json(dc_get.content)
        # This returns the same!!!
        # dc_dto = DomainConfigDTO.from_dict(dc_get_resp.json())
        assert dc_dto.domain == "payments"
        dc_dto.instances = {"test": ["alpha"]}
        dc_put = client.put("/domain-config/payments", json=dc_dto.to_dict())
        assert dc_put.status_code == 204

        dc_get = client.get("/domain-config/payments")
        dc_dto = DomainConfigDTO.from_json(dc_get.content)
        assert dc_dto.instances == {"test": ["alpha"]}

        # 2. Load testset, add duplicate testcase, persist, reload and validate
        ts_get = client.get("/payments/testset")
        assert ts_get.status_code == 200
        ts_list = [TestSetDTO.from_dict(t) for t in ts_get.json()]
        ts_dto = next(t for t in ts_list if t.name == "payments_full")
        assert len(ts_dto.testcases) == 6

        ts_dto.testcases["stage_accounts_SCHEMA_dup"] = TestCaseEntryDTO(
            testobject="stage_accounts",
            testtype=TestType.SCHEMA,
            domain="payments",
            comment="Duplicate schema check",
        )
        assert len(ts_dto.testcases) == 7

        ts_put = client.put(f"/payments/testset/{ts_dto.id}", json=ts_dto.to_dict())
        assert ts_put.status_code == 204

        ts_get = client.get(f"/payments/testset/{ts_dto.testset_id}")
        ts_dto = TestSetDTO.from_json(ts_get.content)
        assert len(ts_dto.testcases) == 7
        assert "stage_accounts_SCHEMA_dup" in ts_dto.testcases

        # 2b. List testobjects via platform endpoint
        pl_get = client.get("/payments/platform/testobjects?stage=test&instance=alpha")
        assert pl_get.status_code == 200
        testobjects = pl_get.json()
        testobject_names = [t["name"] for t in testobjects]
        for tc in ts_dto.testcases.values():
            assert tc.testobject in testobject_names

        # 3. Find specifications
        locations = dc_dto.specifications_locations_by_instance(
            stage="test", instance="alpha"
        )
        request = FindSpecsRequest(testset=ts_dto, locations=locations)
        specs_resp = client.post("/payments/specification/find", json=request.to_dict())
        assert specs_resp.status_code == 200
        spec_list_as_dict = specs_resp.json()
        spec_list = [
            [SpecDTO.from_dict(spec) for spec in inner_list]
            for inner_list in spec_list_as_dict
        ]
        assert len(spec_list) == 7

        # 4. Execute testrun
        request = ExecuteTestRunRequest(
            testset=ts_dto, domain_config=dc_dto, specs=spec_list
        )
        run_resp = client.post("/payments/testrun/", json=request.to_dict())
        assert run_resp.status_code == 202
        testrun_id = run_resp.json()["testrun_id"]

        # 5. Load testrun, convert to DTO, verify every testcase result
        tr_get_resp = client.get(f"/payments/testrun/{testrun_id}")
        assert tr_get_resp.status_code == 200
        tr_dto = TestRunDTO.from_json(tr_get_resp.content)
        assert tr_dto.status.value == "FINISHED"
        assert tr_dto.result.value == "NOK"
        assert len(tr_dto.results) == 7

        _assert_testcase_results(
            [
                (tc.testobject.name, tc.testtype.value, tc.result.value)
                for tc in tr_dto.results
            ],
            self.EXPECTED_RESULTS,
        )
        for tc in tr_dto.results:
            assert tc.status.value == "FINISHED"

        today = datetime.now().strftime("%Y-%m-%d")

        # 6. Verify testrun reports — by date
        tr_report_get_resp = client.get(f"/payments/testrun-report/?date={today}")
        assert tr_report_get_resp.status_code == 200
        tr_reports = [TestRunReportDTO.from_dict(r) for r in tr_report_get_resp.json()]
        tr_report = next(r for r in tr_reports if str(r.testrun_id) == testrun_id)
        assert tr_report.result == "NOK"

        _assert_testcase_results(
            [
                (tc.testobject, tc.testtype, tc.result)
                for tc in tr_report.testcase_results
            ],
            self.EXPECTED_RESULTS,
        )

        # 7. Verify testcase reports — by testrun_id
        tc_trid_get_resp = client.get(
            f"/payments/testcase-report/?testrun_id={testrun_id}"
        )
        assert tc_trid_get_resp.status_code == 200
        tc_reports_by_trid = [
            TestCaseReportDTO.from_dict(r) for r in tc_trid_get_resp.json()
        ]
        assert len(tc_reports_by_trid) == 7

        _assert_testcase_results(
            [(r.testobject, r.testtype, r.result) for r in tc_reports_by_trid],
            self.EXPECTED_RESULTS,
        )
        assert sum(1 for r in tc_reports_by_trid if r.result == "NOK") == 1

        # 8. Verify testcase reports — by date
        tc_date_get_resp = client.get(f"/payments/testcase-report/?date={today}")
        assert tc_date_get_resp.status_code == 200
        tc_reports_by_date = [
            TestCaseReportDTO.from_dict(r)
            for r in tc_date_get_resp.json()
            if r["testrun_id"] == testrun_id
        ]
        assert len(tc_reports_by_date) == 7
