"""
Integration tests for the FastAPI HTTP backend.

Tests the full pipeline against the demo backend, following the same
setup pattern as test_cli_app.py.
"""

from datetime import datetime
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from src.apps.http_app import create_app
from src.apps.http_di import HttpDependencyInjector
from src.config import Config
from src.domain_ports import SaveTestSetCommand
from src.dtos import (
    DomainConfigDTO,
    TestCaseReportDTO,
    TestRunDTO,
    TestRunReportDTO,
    TestSetDTO,
    TestCaseEntryDTO,
    TestType,
)
from tests.fixtures.demo.prepare_demo_artifacts import (
    clean_up_demo_artifacts,
    prepare_demo_artifacts,
)
from tests.fixtures.demo.prepare_demo_data import prepare_demo_data

_DEMO_DIR = Path(__file__).parent / "_demo_data_http"


def _make_config() -> Config:
    return Config(
        DATATESTER_DATA_PLATFORM="DEMO",
        DATATESTER_USER_STORAGE_ENGINE="LOCAL",
        DATATESTER_INTERNAL_STORAGE_LOCATION=f"local://{_DEMO_DIR}/internal/",
        DATATESTER_DEMO_RAW_PATH=str(_DEMO_DIR / "raw"),
        DATATESTER_DEMO_DB_PATH=str(_DEMO_DIR / "dbs"),
    )


@pytest.fixture(scope="module")
def demo_client():
    clean_up_demo_artifacts(_DEMO_DIR)
    prepare_demo_data(_DEMO_DIR)
    prepare_demo_artifacts(_DEMO_DIR)

    config = _make_config()
    di = HttpDependencyInjector(config)

    dc_driver = di.domain_config_driver()
    configs_dir = _DEMO_DIR / "configs"
    for cfg_file in sorted(configs_dir.glob("*.json")):
        dto = DomainConfigDTO.from_json(cfg_file.read_text())
        dc_driver.save_domain_config(config=dto)

    ts_driver = di.testset_driver()
    testsets_dir = _DEMO_DIR / "testsets"
    for ts_file in sorted(testsets_dir.rglob("*.json")):
        dto = TestSetDTO.from_json(ts_file.read_text())
        ts_driver.adapter.save_testset(SaveTestSetCommand(testset=dto))

    app = create_app(config)
    with TestClient(app) as client:
        yield client

    clean_up_demo_artifacts(_DEMO_DIR)


class TestDomainConfigEndpoints:
    def test_list_domain_configs_returns_200(self, demo_client: TestClient):
        response = demo_client.get("/domain-config")
        assert response.status_code == 200
        data = response.json()
        assert "payments" in data
        assert "sales" in data

    def test_load_domain_config_returns_200(self, demo_client: TestClient):
        response = demo_client.get("/domain-config/payments")
        assert response.status_code == 200
        data = response.json()
        assert data["domain"] == "payments"

    def test_put_domain_config_returns_204(self, demo_client: TestClient):
        get_resp = demo_client.get("/domain-config/payments")
        assert get_resp.status_code == 200
        dto = get_resp.json()
        put_resp = demo_client.put("/domain-config/payments", json=dto)
        assert put_resp.status_code == 204


class TestTestSetEndpoints:
    def test_list_testsets_returns_200(self, demo_client: TestClient):
        response = demo_client.get("/payments/testset")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    def test_load_testset_returns_200(self, demo_client: TestClient):
        list_resp = demo_client.get("/payments/testset")
        testsets = list_resp.json()
        testset_id = testsets[0]["testset_id"]
        response = demo_client.get(f"/payments/testset/{testset_id}")
        assert response.status_code == 200
        assert response.json()["testset_id"] == testset_id


class TestTestRunEndpoints:
    def test_list_testruns_returns_200(self, demo_client: TestClient):
        response = demo_client.get("/payments/testrun/")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_post_testrun_returns_202_with_testrun_id(self, demo_client: TestClient):
        # Get domain config
        dc_resp = demo_client.get("/domain-config/payments")
        domain_config = dc_resp.json()

        # Get testset
        ts_resp = demo_client.get("/payments/testset")
        testsets = ts_resp.json()
        testset = next(t for t in testsets if t["name"] == "payments_full")

        # Find specifications
        specs_locations = domain_config["specifications_locations"]
        if isinstance(specs_locations, dict):
            locations = list(specs_locations.values())
            if locations and isinstance(locations[0], list):
                locations = locations[0]
        elif isinstance(specs_locations, list):
            locations = specs_locations
        else:
            locations = [specs_locations]
        find_body = {"testset": testset, "locations": locations}
        specs_resp = demo_client.post("/payments/specification/find", json=find_body)
        assert specs_resp.status_code == 200
        spec_list = specs_resp.json()

        # Execute testrun
        body = {
            "testset": testset,
            "domain_config": domain_config,
            "spec_list": spec_list,
        }
        response = demo_client.post("/payments/testrun/", json=body)
        assert response.status_code == 202
        data = response.json()
        assert "testrun_id" in data
        return data["testrun_id"]

    def test_load_testrun_returns_200_after_execution(self, demo_client: TestClient):
        # Get domain config
        dc_resp = demo_client.get("/domain-config/payments")
        domain_config = dc_resp.json()

        # Get testset
        ts_resp = demo_client.get("/payments/testset")
        testsets = ts_resp.json()
        testset = next(t for t in testsets if t["name"] == "payments_full")

        # Find specifications
        specs_locations = domain_config["specifications_locations"]
        if isinstance(specs_locations, dict):
            locations = list(specs_locations.values())
            if locations and isinstance(locations[0], list):
                locations = locations[0]
        elif isinstance(specs_locations, list):
            locations = specs_locations
        else:
            locations = [specs_locations]
        find_body = {"testset": testset, "locations": locations}
        specs_resp = demo_client.post("/payments/specification/find", json=find_body)
        spec_list = specs_resp.json()

        # Execute testrun
        body = {
            "testset": testset,
            "domain_config": domain_config,
            "spec_list": spec_list,
        }
        response = demo_client.post("/payments/testrun/", json=body)
        assert response.status_code == 202
        testrun_id = response.json()["testrun_id"]

        # TestClient runs background tasks synchronously, so load immediately
        get_resp = demo_client.get(f"/payments/testrun/{testrun_id}")
        assert get_resp.status_code == 200
        assert get_resp.json()["testrun_id"] == testrun_id


class TestPlatformEndpoints:
    def test_list_testobjects_payments(self, demo_client: TestClient):
        response = demo_client.get(
            "/payments/platform/testobjects?stage=test&instance=alpha"
        )
        assert response.status_code == 200
        data = response.json()
        names = [t["name"] for t in data]
        assert "stage_accounts" in names
        assert "raw_accounts" in names
        for t in data:
            assert t["domain"] == "payments"
            assert t["stage"] == "test"
            assert t["instance"] == "alpha"

    def test_list_testobjects_sales(self, demo_client: TestClient):
        response = demo_client.get("/sales/platform/testobjects?stage=test&instance=main")
        assert response.status_code == 200
        data = response.json()
        names = [t["name"] for t in data]
        assert "stage_customers" in names
        assert "core_customer_transactions" in names

    def test_list_testobjects_requires_stage_and_instance(self, demo_client: TestClient):
        response = demo_client.get("/payments/platform/testobjects")
        assert response.status_code == 422


def _assert_testcase_results(
    results: list[tuple[str, str, str]],
    expected: list[tuple[str, str, str]],
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

    def test_full_flow(self, demo_client: TestClient):
        # 1. Load domain config, modify, persist, reload and validate
        dc_get_resp = demo_client.get("/domain-config/payments")
        assert dc_get_resp.status_code == 200
        dc_dto = DomainConfigDTO.from_json(dc_get_resp.content)
        assert dc_dto.domain == "payments"

        dc_dto.instances = {"test": ["alpha"]}
        dc_put_resp = demo_client.put(
            "/domain-config/payments", json=dc_dto.to_dict(mode="json")
        )
        assert dc_put_resp.status_code == 204

        dc_get_resp = demo_client.get("/domain-config/payments")
        dc_dto = DomainConfigDTO.from_json(dc_get_resp.content)
        assert dc_dto.instances == {"test": ["alpha"]}

        # 2. Load testset, add duplicate testcase, persist, reload and validate
        ts_get_resp = demo_client.get("/payments/testset")
        assert ts_get_resp.status_code == 200
        ts_list = [TestSetDTO.from_dict(t) for t in ts_get_resp.json()]
        ts_dto = next(t for t in ts_list if t.name == "payments_full")
        assert len(ts_dto.testcases) == 6

        ts_dto.testcases["stage_accounts_SCHEMA_dup"] = TestCaseEntryDTO(
            testobject="stage_accounts",
            testtype=TestType.SCHEMA,
            domain="payments",
            comment="Duplicate schema check",
        )
        assert len(ts_dto.testcases) == 7

        ts_put_resp = demo_client.put(
            f"/payments/testset/{ts_dto.testset_id}",
            json=ts_dto.to_dict(mode="json"),
        )
        assert ts_put_resp.status_code == 204

        ts_get_resp = demo_client.get(f"/payments/testset/{ts_dto.testset_id}")
        ts_dto = TestSetDTO.from_json(ts_get_resp.content)
        assert len(ts_dto.testcases) == 7
        assert "stage_accounts_SCHEMA_dup" in ts_dto.testcases

        # 2b. List testobjects via platform endpoint
        platform_resp = demo_client.get(
            "/payments/platform/testobjects?stage=test&instance=alpha"
        )
        assert platform_resp.status_code == 200
        testobjects = platform_resp.json()
        testobject_names = [t["name"] for t in testobjects]
        for tc in ts_dto.testcases.values():
            assert tc.testobject in testobject_names, (
                f"Testobject {tc.testobject} not found in platform"
            )

        # 3. Find specifications using DomainConfigDTO method
        locations = dc_dto.specifications_locations_by_instance(
            stage="test", instance="alpha"
        )
        locations_json = [loc.model_dump() for loc in locations]
        specs_resp = demo_client.post(
            "/payments/specification/find",
            json={"testset": ts_dto.to_dict(mode="json"), "locations": locations_json},
        )
        assert specs_resp.status_code == 200
        spec_list = specs_resp.json()
        assert len(spec_list) == 7

        # 4. Execute testrun
        run_resp = demo_client.post(
            "/payments/testrun/",
            json={
                "testset": ts_dto.to_dict(mode="json"),
                "domain_config": dc_dto.to_dict(mode="json"),
                "spec_list": spec_list,
            },
        )
        assert run_resp.status_code == 202
        testrun_id = run_resp.json()["testrun_id"]

        # 5. Load testrun, convert to DTO, verify every testcase result
        tr_get_resp = demo_client.get(f"/payments/testrun/{testrun_id}")
        assert tr_get_resp.status_code == 200
        tr_dto = TestRunDTO.from_json(tr_get_resp.content)
        assert tr_dto.status.value == "FINISHED"
        assert tr_dto.result.value == "NOK"
        assert len(tr_dto.testcase_results) == 7

        _assert_testcase_results(
            [
                (tc.testobject.name, tc.testtype.value, tc.result.value)
                for tc in tr_dto.testcase_results
            ],
            self.EXPECTED_RESULTS,
        )
        for tc in tr_dto.testcase_results:
            assert tc.status.value == "FINISHED"

        today = datetime.now().strftime("%Y-%m-%d")

        # 6. Verify testrun reports — by date
        tr_report_get_resp = demo_client.get(f"/payments/testrun-report/?date={today}")
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
        tc_trid_get_resp = demo_client.get(
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
        tc_date_get_resp = demo_client.get(f"/payments/testcase-report/?date={today}")
        assert tc_date_get_resp.status_code == 200
        tc_reports_by_date = [
            TestCaseReportDTO.from_dict(r)
            for r in tc_date_get_resp.json()
            if r["testrun_id"] == testrun_id
        ]
        assert len(tc_reports_by_date) == 7
