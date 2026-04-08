from typing import List

from nicegui import app

from src.client_interface import DomainConfigDTO, TestObjectDTO, TestRunDTO, TestSetDTO
from src.client_interface.requests import FindSpecsRequest
from src.dtos import TestRunDefDTO
from src.ui.common import Status
from src.ui.client import BackendError, DataTesterClient

from .state import State


class Controller:
    """
    UI Controller and state machine.
    All state access and modification MUST go through Controller.
    """

    def __init__(self, client: DataTesterClient, state: State) -> None:
        self._client: DataTesterClient = client
        self.state: State = state

    # --- domain ---

    @property
    def domain(self) -> str | None:
        return self.state.domain

    @domain.setter
    def domain(self, val: str) -> None:
        self.state.domain = val

    @property
    def domains(self) -> List[str]:
        return self.state.domains

    # --- accessors ---

    def domain_configs(self) -> dict[str, DomainConfigDTO]:
        return self.state.domain_configs

    def get_domain_config_status(self, domain: str) -> Status:
        return self.state.domain_configs_status.get(domain, Status.UNCLEAR)

    def testsets(self, domain: str) -> List[TestSetDTO]:
        return self.state.testsets.get(domain, [])

    def get_testset_status(self, domain: str) -> Status:
        return self.state.testsets_status.get(domain, Status.UNCLEAR)

    def testobjects(self, domain: str) -> List[TestObjectDTO]:
        return self.state.testobjects.get(domain, [])

    def get_testobjects_status(self, domain: str) -> Status:
        return self.state.testobjects_status.get(domain, Status.UNCLEAR)

    def testruns(self, domain: str) -> List[TestRunDTO]:
        return self.state.testruns.get(domain, [])

    def get_testruns_status(self, domain: str) -> Status:
        return self.state.testruns_status.get(domain, Status.UNCLEAR)

    def specs(self, domain: str) -> List[TestRunDefDTO]:
        return self.state.specs.get(domain, [])

    def get_specs_status(self, domain: str) -> Status:
        return self.state.specs_status.get(domain, Status.UNCLEAR)

    # --- load methods ---

    async def load_domains(self) -> str | None:
        """Fetch domain configs from backend. Returns error message or None."""
        try:
            configs = await self._client.get_domain_configs()
            self.state.domain_configs = configs
            self.state.domains = list(configs.keys())
            return None
        except BackendError as exc:
            return f"Backend error {exc.status_code}: {exc.detail}"
        except Exception as exc:
            return f"Could not reach backend: {exc}"

    async def load_testsets(self, domain: str) -> str | None:
        """Fetch testsets for a domain. Returns error message or None."""
        self.state.set_testsets_status(domain, Status.LOADING)
        try:
            testsets = await self._client.get_testsets(domain)
            self.state.set_testsets(domain, testsets)
            self.state.set_testsets_status(domain, Status.LOADED)
            return None
        except BackendError as exc:
            self.state.set_testsets_status(domain, Status.ERROR)
            return f"Backend error {exc.status_code}: {exc.detail}"
        except Exception as exc:
            self.state.set_testsets_status(domain, Status.ERROR)
            return f"Could not reach backend: {exc}"

    async def load_testobjects(self, domain: str) -> str | None:
        """Fetch testobjects for all stage/instance combos of a domain."""
        self.state.set_testobjects_status(domain, Status.LOADING)
        try:
            domain_config = self.state.domain_configs[domain]
            all_testobjects: List[TestObjectDTO] = []
            for stage, instances in domain_config.instances.items():
                for instance in instances:
                    objects = await self._client.get_testobjects(domain, stage, instance)
                    all_testobjects.extend(objects)
            self.state.set_testobjects(domain, all_testobjects)
            self.state.set_testobjects_status(domain, Status.LOADED)
            return None
        except BackendError as exc:
            self.state.set_testobjects_status(domain, Status.ERROR)
            return f"Backend error {exc.status_code}: {exc.detail}"
        except Exception as exc:
            self.state.set_testobjects_status(domain, Status.ERROR)
            return f"Could not reach backend: {exc}"

    async def load_testruns(self, domain: str) -> str | None:
        """Fetch all testruns for a domain."""
        self.state.set_testruns_status(domain, Status.LOADING)
        try:
            testruns = await self._client.get_testruns(domain)
            self.state.set_testruns(domain, testruns)
            self.state.set_testruns_status(domain, Status.LOADED)
            return None
        except BackendError as exc:
            self.state.set_testruns_status(domain, Status.ERROR)
            return f"Backend error {exc.status_code}: {exc.detail}"
        except Exception as exc:
            self.state.set_testruns_status(domain, Status.ERROR)
            return f"Could not reach backend: {exc}"

    async def load_specs(self, domain: str) -> str | None:
        """Find specs for all testsets of a domain. Requires testsets to be loaded."""
        self.state.set_specs_status(domain, Status.LOADING)
        try:
            domain_config = self.state.domain_configs[domain]
            testsets = self.state.testsets.get(domain, [])
            app.storage.general.setdefault("specs", {})[domain] = []
            for testset in testsets:
                request = FindSpecsRequest(testset=testset, domain_config=domain_config)
                trd = await self._client.find_specs(domain, request)
                self.state.set_specs(domain, trd)
            self.state.set_specs_status(domain, Status.LOADED)
            return None
        except BackendError as exc:
            self.state.set_specs_status(domain, Status.ERROR)
            return f"Backend error {exc.status_code}: {exc.detail}"
        except Exception as exc:
            self.state.set_specs_status(domain, Status.ERROR)
            return f"Could not reach backend: {exc}"

    async def load_backend_data(self, domain: str) -> str | None:
        """Load domain configs then all objects for the given domain.

        Returns the first error message encountered, or None on full success.
        """
        error = await self.load_domains()
        if error:
            self.state.set_domain_config_status(domain, Status.ERROR)
            return error
        self.state.set_domain_config_status(domain, Status.LOADED)

        await self.load_testsets(domain)
        await self.load_testobjects(domain)
        await self.load_testruns(domain)
        await self.load_specs(domain)
        return None
