from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Dict, List

from nicegui import app

from src.client_interface import DomainConfigDTO, TestObjectDTO, TestRunDTO, TestSetDTO
from src.dtos import SpecEntryDTO
from src.ui.common import Status


class StateError(Exception):
    """"""


class State(ABC):
    """Typed state contract. Each property maps to a named object in a storage scope.

    storage.general: domain_configs, domains, testsets, testobjects, testruns, specs
                     + per-domain statuses for each
    storage.user:    domain
    """

    # --- storage.general ---

    @property
    @abstractmethod
    def domain_configs(self) -> Dict[str, DomainConfigDTO]:
        pass

    @domain_configs.setter
    @abstractmethod
    def domain_configs(self, val: Dict[str, DomainConfigDTO]) -> None:
        pass

    @property
    @abstractmethod
    def domains(self) -> List[str]:
        pass

    @domains.setter
    @abstractmethod
    def domains(self, val: List[str]) -> None:
        pass

    @property
    @abstractmethod
    def domain_configs_status(self) -> Dict[str, Status]:
        pass

    @abstractmethod
    def set_domain_config_status(self, domain: str, status: Status) -> None:
        pass

    @property
    @abstractmethod
    def testsets(self) -> Dict[str, List[TestSetDTO]]:
        pass

    @abstractmethod
    def set_testsets(self, domain: str, testsets: List[TestSetDTO]) -> None:
        pass

    @property
    @abstractmethod
    def testsets_status(self) -> Dict[str, Status]:
        pass

    @abstractmethod
    def set_testsets_status(self, domain: str, status: Status) -> None:
        pass

    @property
    @abstractmethod
    def testobjects(self) -> Dict[str, List[TestObjectDTO]]:
        pass

    @abstractmethod
    def set_testobjects(self, domain: str, testobjects: List[TestObjectDTO]) -> None:
        pass

    @property
    @abstractmethod
    def testobjects_status(self) -> Dict[str, Status]:
        pass

    @abstractmethod
    def set_testobjects_status(self, domain: str, status: Status) -> None:
        pass

    @property
    @abstractmethod
    def testruns(self) -> Dict[str, List[TestRunDTO]]:
        pass

    @abstractmethod
    def set_testruns(self, domain: str, testruns: List[TestRunDTO]) -> None:
        pass

    @property
    @abstractmethod
    def testruns_status(self) -> Dict[str, Status]:
        pass

    @abstractmethod
    def set_testruns_status(self, domain: str, status: Status) -> None:
        pass

    @abstractmethod
    def specs(self, domain: str) -> Dict[str, List[SpecEntryDTO]]:
        """stage → List[SpecEntryDTO]: specs discovered for the given domain."""
        pass

    @abstractmethod
    def set_specs(self, domain: str, stage: str, entries: List[SpecEntryDTO]) -> None:
        pass

    @property
    @abstractmethod
    def specs_status(self) -> Dict[str, Status]:
        pass

    @abstractmethod
    def set_specs_status(self, domain: str, status: Status) -> None:
        pass

    # --- storage.user ---

    @property
    @abstractmethod
    def domain(self) -> str | None:
        pass

    @domain.setter
    @abstractmethod
    def domain(self, val: str) -> None:
        pass

    @property
    @abstractmethod
    def domain_config(self) -> DomainConfigDTO:
        pass

    @domain_config.setter
    @abstractmethod
    def domain_config(self, val: DomainConfigDTO) -> None:
        pass


class NiceGuiState(State):
    """Concrete State backed by app.storage.*. Never caches storage objects."""

    # --- storage.general ---

    @property
    def domain_configs(self) -> Dict[str, DomainConfigDTO]:
        cfgs_ = app.storage.general.get("domain_configs", {})
        return {k: DomainConfigDTO.model_validate(v) for k, v in cfgs_.items()}

    @domain_configs.setter
    def domain_configs(self, val: Dict[str, DomainConfigDTO]) -> None:
        app.storage.general["domain_configs"] = {k: v.to_dict() for k, v in val.items()}

    @property
    def domains(self) -> List[str]:
        return app.storage.general.get("domains", [])

    @domains.setter
    def domains(self, value: List[str]) -> None:
        app.storage.general["domains"] = value

    @property
    def domain_configs_status(self) -> Dict[str, Status]:
        raw = app.storage.general.get("domain_configs_status", {})
        return {d: Status(s) for d, s in raw.items()}

    def set_domain_config_status(self, domain: str, status: Status) -> None:
        app.storage.general.setdefault("domain_configs_status", {})[domain] = status.value

    @property
    def testsets(self) -> Dict[str, List[TestSetDTO]]:
        ts_ = app.storage.general.get("testsets", {})
        return {
            domain: [TestSetDTO.model_validate(v) for v in items]
            for domain, items in ts_.items()
        }

    def set_testsets(self, domain: str, testsets: List[TestSetDTO]) -> None:
        app.storage.general.setdefault("testsets", {})[domain] = [
            t.to_dict() for t in testsets
        ]

    @property
    def testsets_status(self) -> Dict[str, Status]:
        raw = app.storage.general.get("testsets_status", {})
        return {d: Status(s) for d, s in raw.items()}

    def set_testsets_status(self, domain: str, status: Status) -> None:
        app.storage.general.setdefault("testsets_status", {})[domain] = status.value

    @property
    def testobjects(self) -> Dict[str, List[TestObjectDTO]]:
        raw = app.storage.general.get("testobjects", {})
        return {
            domain: [TestObjectDTO.model_validate(o) for o in items]
            for domain, items in raw.items()
        }

    def set_testobjects(self, domain: str, testobjects: List[TestObjectDTO]) -> None:
        app.storage.general.setdefault("testobjects", {})[domain] = [
            o.to_dict() for o in testobjects
        ]

    @property
    def testobjects_status(self) -> Dict[str, Status]:
        raw = app.storage.general.get("testobjects_status", {})
        return {d: Status(s) for d, s in raw.items()}

    def set_testobjects_status(self, domain: str, status: Status) -> None:
        app.storage.general.setdefault("testobjects_status", {})[domain] = status.value

    @property
    def testruns(self) -> Dict[str, List[TestRunDTO]]:
        raw = app.storage.general.get("testruns", {})
        return {
            domain: [TestRunDTO.model_validate(r) for r in items]
            for domain, items in raw.items()
        }

    def set_testruns(self, domain: str, testruns: List[TestRunDTO]) -> None:
        app.storage.general.setdefault("testruns", {})[domain] = [
            r.to_dict() for r in testruns
        ]

    @property
    def testruns_status(self) -> Dict[str, Status]:
        raw = app.storage.general.get("testruns_status", {})
        return {d: Status(s) for d, s in raw.items()}

    def set_testruns_status(self, domain: str, status: Status) -> None:
        app.storage.general.setdefault("testruns_status", {})[domain] = status.value

    def specs(self, domain: str) -> Dict[str, List[SpecEntryDTO]]:
        """stage → List[SpecEntryDTO]: specs discovered for the given domain.
        Only entries with at least one non-empty spec attached are stored."""
        raw = app.storage.general.get("specs", {}).get(domain, {})
        return {
            stage: [SpecEntryDTO.model_validate(e) for e in entries]
            for stage, entries in raw.items()
        }

    def set_specs(self, domain: str, stage: str, entries: List[SpecEntryDTO]) -> None:
        """Overwrite spec entries for domain/stage. Other stages are untouched."""
        (app.storage.general.setdefault("specs", {}).setdefault(domain, {})[stage]) = [
            e.model_dump(mode="json") for e in entries
        ]

    @property
    def specs_status(self) -> Dict[str, Status]:
        raw = app.storage.general.get("specs_status", {})
        return {d: Status(s) for d, s in raw.items()}

    def set_specs_status(self, domain: str, status: Status) -> None:
        app.storage.general.setdefault("specs_status", {})[domain] = status.value

    # --- storage.user ---

    @property
    def domain(self) -> str | None:
        return app.storage.user.get("domain")

    @domain.setter
    def domain(self, val: str | None) -> None:
        if val not in self.domain_configs:
            raise StateError(f"Domain {val} doesn't exist")
        app.storage.user["domain"] = val

    @property
    def domain_config(self) -> DomainConfigDTO:
        domain_selection = self.domain
        if domain_selection is None:
            raise StateError("No domain is selected.")
        return self.domain_configs[domain_selection]

    @domain_config.setter
    def domain_config(self, val: DomainConfigDTO) -> None:
        if self.domain is None:
            raise StateError("Can not set domain config: No domain is selected")
        if val.domain not in self.domain_configs:
            raise StateError("Can not set domain config: domain not in backend DTOs")
        self.domain_config = val
