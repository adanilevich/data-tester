from __future__ import annotations

import time

from nicegui import app

from src.dtos import DomainConfigDTO, SpecEntryDTO, TestObjectDTO, TestRunDTO, TestSetDTO
from src.ui.common import Status
from src.ui.controller.state import State, StateError


class NiceGuiState(State):
    """
    Concrete State backed by app.storage.*. Never caches storage objects.
    We specifically use app.storage.general for objects which are loaded from backend
    and reused across users of a domain. DO NOT change this to app.storage.user
    """

    @property
    def domain_configs(self) -> dict[str, DomainConfigDTO]:
        cfgs_ = app.storage.general.get("domain_configs", {})
        return {k: DomainConfigDTO.model_validate(v) for k, v in cfgs_.items()}

    @domain_configs.setter
    def domain_configs(self, val: dict[str, DomainConfigDTO]) -> None:
        app.storage.general["domain_configs"] = {k: v.to_dict() for k, v in val.items()}

    @property
    def domains(self) -> list[str]:
        return app.storage.general.get("domains", [])

    @domains.setter
    def domains(self, value: list[str]) -> None:
        app.storage.general["domains"] = value

    @property
    def domain_configs_status(self) -> dict[str, Status]:
        raw = app.storage.user.get("domain_configs_status", {})
        return {d: Status(s) for d, s in raw.items()}

    def set_domain_config_status(self, domain: str, status: Status) -> None:
        current = dict(app.storage.user.get("domain_configs_status", {}))
        current[domain] = status.value
        app.storage.user["domain_configs_status"] = current

    @property
    def testsets(self) -> dict[str, list[TestSetDTO]]:
        ts_ = app.storage.general.get("testsets", {})
        return {
            domain: [TestSetDTO.model_validate(v) for v in items]
            for domain, items in ts_.items()
        }

    def set_testsets(self, domain: str, testsets: list[TestSetDTO]) -> None:
        current = dict(app.storage.general.get("testsets", {}))
        current[domain] = [t.to_dict() for t in testsets]
        app.storage.general["testsets"] = current

    @property
    def testsets_status(self) -> dict[str, Status]:
        raw = app.storage.user.get("testsets_status", {})
        return {d: Status(s) for d, s in raw.items()}

    def set_testsets_status(self, domain: str, status: Status) -> None:
        current = dict(app.storage.user.get("testsets_status", {}))
        current[domain] = status.value
        app.storage.user["testsets_status"] = current

    @property
    def testobjects(self) -> dict[str, list[TestObjectDTO]]:
        raw = app.storage.general.get("testobjects", {})
        return {
            domain: [TestObjectDTO.model_validate(o) for o in items]
            for domain, items in raw.items()
        }

    def set_testobjects(self, domain: str, testobjects: list[TestObjectDTO]) -> None:
        current = dict(app.storage.general.get("testobjects", {}))
        current[domain] = [o.to_dict() for o in testobjects]
        app.storage.general["testobjects"] = current

    @property
    def testobjects_status(self) -> dict[str, Status]:
        raw = app.storage.user.get("testobjects_status", {})
        return {d: Status(s) for d, s in raw.items()}

    def set_testobjects_status(self, domain: str, status: Status) -> None:
        current = dict(app.storage.user.get("testobjects_status", {}))
        current[domain] = status.value
        app.storage.user["testobjects_status"] = current

    @property
    def testruns(self) -> dict[str, list[TestRunDTO]]:
        raw = app.storage.general.get("testruns", {})
        return {
            domain: [TestRunDTO.model_validate(r) for r in items]
            for domain, items in raw.items()
        }

    def set_testruns(self, domain: str, testruns: list[TestRunDTO]) -> None:
        current = dict(app.storage.general.get("testruns", {}))
        current[domain] = [r.to_dict() for r in testruns]
        app.storage.general["testruns"] = current

    @property
    def testruns_status(self) -> dict[str, Status]:
        raw = app.storage.user.get("testruns_status", {})
        return {d: Status(s) for d, s in raw.items()}

    def set_testruns_status(self, domain: str, status: Status) -> None:
        current = dict(app.storage.user.get("testruns_status", {}))
        current[domain] = status.value
        app.storage.user["testruns_status"] = current

    def specs(self, domain: str) -> dict[str, list[SpecEntryDTO]]:
        raw = app.storage.general.get("specs", {}).get(domain, {})
        return {
            stage: [SpecEntryDTO.model_validate(e) for e in entries]
            for stage, entries in raw.items()
        }

    def set_specs(
        self, domain: str, stage: str, entries: list[SpecEntryDTO]
    ) -> None:
        outer = dict(app.storage.general.get("specs", {}))
        inner = dict(outer.get(domain, {}))
        inner[stage] = [e.model_dump(mode="json") for e in entries]
        outer[domain] = inner
        app.storage.general["specs"] = outer

    @property
    def specs_status(self) -> dict[str, Status]:
        raw = app.storage.user.get("specs_status", {})
        return {d: Status(s) for d, s in raw.items()}

    def set_specs_status(self, domain: str, status: Status) -> None:
        current = dict(app.storage.user.get("specs_status", {}))
        current[domain] = status.value
        app.storage.user["specs_status"] = current

    @property
    def domain(self) -> str | None:
        return app.storage.user.get("domain")

    @domain.setter
    def domain(self, val: str | None) -> None:
        if val is not None and val not in self.domain_configs:
            raise StateError(f"Domain {val} doesn't exist")
        app.storage.user["domain"] = val

    @property
    def domain_config(self) -> DomainConfigDTO:
        domain_selection = self.domain
        if domain_selection is None:
            raise StateError("No domain is selected.")
        return self.domain_configs[domain_selection]

    def preliminary_testruns(self, domain: str) -> list[TestRunDTO]:
        raw = app.storage.user.get("preliminary_testruns", {}).get(domain, {})
        return [TestRunDTO.model_validate(r) for r in raw.values()]

    def add_preliminary_testrun(self, domain: str, testrun: TestRunDTO) -> None:
        outer = dict(app.storage.user.get("preliminary_testruns", {}))
        inner = dict(outer.get(domain, {}))
        inner[str(testrun.id)] = testrun.to_dict()
        outer[domain] = inner
        app.storage.user["preliminary_testruns"] = outer

    def remove_preliminary_testrun(self, domain: str, testrun_id: str) -> None:
        outer = dict(app.storage.user.get("preliminary_testruns", {}))
        inner = dict(outer.get(domain, {}))
        inner.pop(testrun_id, None)
        outer[domain] = inner
        app.storage.user["preliminary_testruns"] = outer

    def get_last_loaded(self, domain: str, data_type: str) -> float | None:
        return app.storage.general.get("last_loaded", {}).get(f"{domain}_{data_type}")

    def set_last_loaded(self, domain: str, data_type: str) -> None:
        current = dict(app.storage.general.get("last_loaded", {}))
        current[f"{domain}_{data_type}"] = time.time()
        app.storage.general["last_loaded"] = current

    def invalidate_last_loaded(self, domain: str, data_type: str) -> None:
        current = dict(app.storage.general.get("last_loaded", {}))
        current.pop(f"{domain}_{data_type}", None)
        app.storage.general["last_loaded"] = current
