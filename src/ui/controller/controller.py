import logging
from uuid import uuid4

from src.client_interface import (
    DomainConfigDTO,
    TestCaseEntryDTO,
    TestObjectDTO,
    TestRunDTO,
    TestSetDTO,
)
from src.client_interface.requests import FindSpecsRequest
from src.dtos import SpecEntryDTO, TestType
from src.ui.common import Status
from src.ui.client import BackendError, DataTesterClient

from .state import State

_log = logging.getLogger("datatester")


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
    def domain(self, val: str | None) -> None:
        self.state.domain = val

    @property
    def domains(self) -> list[str]:
        return self.state.domains

    # --- accessors ---

    def domain_configs(self) -> dict[str, DomainConfigDTO]:
        return self.state.domain_configs

    def get_domain_config_status(self, domain: str) -> Status:
        return self.state.domain_configs_status.get(domain, Status.UNCLEAR)

    def testsets(self, domain: str) -> list[TestSetDTO]:
        return self.state.testsets.get(domain, [])

    def get_testset_status(self, domain: str) -> Status:
        return self.state.testsets_status.get(domain, Status.UNCLEAR)

    def testobjects(self, domain: str) -> list[TestObjectDTO]:
        return self.state.testobjects.get(domain, [])

    def get_testobjects_status(self, domain: str) -> Status:
        return self.state.testobjects_status.get(domain, Status.UNCLEAR)

    def testruns(self, domain: str) -> list[TestRunDTO]:
        return self.state.testruns.get(domain, [])

    def get_testruns_status(self, domain: str) -> Status:
        return self.state.testruns_status.get(domain, Status.UNCLEAR)

    def specs(self, domain: str) -> dict[str, list[SpecEntryDTO]]:
        """stage → List[SpecEntryDTO]: specs discovered for the given domain."""
        return self.state.specs(domain)

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
            err = f"Backend error {exc.status_code}: {exc.detail}"
            _log.error("load_domains: %s", err)
            return err
        except Exception as exc:
            err = f"Could not reach backend: {exc}"
            _log.error("load_domains: %s", err)
            return err

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
            err = f"Backend error {exc.status_code}: {exc.detail}"
            _log.error("load_testsets(%s): %s", domain, err)
            return err
        except Exception as exc:
            self.state.set_testsets_status(domain, Status.ERROR)
            err = f"Could not reach backend: {exc}"
            _log.error("load_testsets(%s): %s", domain, err)
            return err

    async def load_testobjects(self, domain: str) -> str | None:
        """Fetch testobjects for all stage/instance combos of a domain."""
        self.state.set_testobjects_status(domain, Status.LOADING)
        try:
            domain_config = self.state.domain_configs[domain]
            all_testobjects: list[TestObjectDTO] = []
            for stage, instances in domain_config.instances.items():
                for instance in instances:
                    objects = await self._client.get_testobjects(domain, stage, instance)
                    all_testobjects.extend(objects)
            self.state.set_testobjects(domain, all_testobjects)
            self.state.set_testobjects_status(domain, Status.LOADED)
            return None
        except BackendError as exc:
            self.state.set_testobjects_status(domain, Status.ERROR)
            err = f"Backend error {exc.status_code}: {exc.detail}"
            _log.error("load_testobjects(%s): %s", domain, err)
            return err
        except Exception as exc:
            self.state.set_testobjects_status(domain, Status.ERROR)
            err = f"Could not reach backend: {exc}"
            _log.error("load_testobjects(%s): %s", domain, err)
            return err

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
            err = f"Backend error {exc.status_code}: {exc.detail}"
            _log.error("load_testruns(%s): %s", domain, err)
            return err
        except Exception as exc:
            self.state.set_testruns_status(domain, Status.ERROR)
            err = f"Could not reach backend: {exc}"
            _log.error("load_testruns(%s): %s", domain, err)
            return err

    async def load_specs(self, domain: str) -> str | None:
        """Discover specs for every testobject on the platform, grouped by stage.

        Builds one ephemeral TestSetDTO per stage (one TestCaseEntryDTO per
        testobject × TestType). Drops entries with no specs found.
        Specs are stage-level so one representative instance per stage suffices.
        """
        self.state.set_specs_status(domain, Status.LOADING)
        try:
            domain_config = self.state.domain_configs[domain]
            all_testobjects = self.state.testobjects.get(domain, [])

            # Collect unique testobject names per stage; record one representative
            # instance. Specs are stored per stage only so any instance works.
            stage_instance: dict[str, str] = {}  # stage → representative instance
            stage_testobject_names: dict[str, set[str]] = {}  # stage → testobject names
            for obj in all_testobjects:
                if obj.stage not in stage_instance:  # first time we see this stage
                    stage_instance[obj.stage] = obj.instance
                    stage_testobject_names[obj.stage] = set()
                stage_testobject_names[obj.stage].add(obj.name)

            # All types except those without naming conventions:
            # ABSTRACT, UNKNOWN, DUMMY_*.
            _IGNORED_TESTTYPES = {
                TestType.ABSTRACT,
                TestType.UNKNOWN,
                TestType.DUMMY_OK,
                TestType.DUMMY_NOK,
                TestType.DUMMY_EXCEPTION,
            }
            _TESTTYPES = [tt for tt in TestType if tt not in _IGNORED_TESTTYPES]

            for stage, instance in stage_instance.items():  # one testset per stage
                testcases = {
                    f"{name}_{tt.value}": TestCaseEntryDTO(
                        testobject=name, testtype=tt, domain=domain
                    )
                    for name in stage_testobject_names[stage]
                    for tt in _TESTTYPES
                }
                testset = TestSetDTO(
                    testset_id=uuid4(),
                    name=f"{domain}_{stage}_discovery",
                    domain=domain,
                    default_stage=stage,
                    default_instance=instance,
                    testcases=testcases,
                )
                request = FindSpecsRequest(testset=testset, domain_config=domain_config)
                testrun_def = await self._client.find_specs(domain, request)
                entries: list[SpecEntryDTO] = []
                for testcase_def in testrun_def.testcase_defs:
                    all_specs = [spec for spec in testcase_def.specs]
                    non_empty_specs = [spec for spec in all_specs if not spec.empty]
                    if non_empty_specs:
                        entries.append(
                            SpecEntryDTO(
                                testobject_name=testcase_def.testobject.name,
                                testtype=testcase_def.testtype,
                                scenario=testcase_def.scenario,
                                specs=non_empty_specs,
                            )
                        )
                self.state.set_specs(domain, stage, entries)

            self.state.set_specs_status(domain, Status.LOADED)
            return None
        except BackendError as exc:
            self.state.set_specs_status(domain, Status.ERROR)
            err = f"Backend error {exc.status_code}: {exc.detail}"
            _log.error("load_specs(%s): %s", domain, err)
            return err
        except Exception as exc:
            self.state.set_specs_status(domain, Status.ERROR)
            err = f"Could not reach backend: {exc}"
            _log.error("load_specs(%s): %s", domain, err)
            return err

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

        if self.domain != domain:
            self.domain = domain
        return None

    async def save_config(self, domain: str, dto: DomainConfigDTO) -> str | None:
        """Save domain config via PUT. Updates state on success.

        Returns error string or None on success.
        """
        try:
            await self._client.save_domain_config(domain, dto)
            configs = self.state.domain_configs
            configs[domain] = dto
            self.state.domain_configs = configs
            return None
        except BackendError as exc:
            err = f"Backend error {exc.status_code}: {exc.detail}"
            _log.error("save_config(%s): %s", domain, err)
            return err
        except Exception as exc:
            err = f"Could not reach backend: {exc}"
            _log.error("save_config(%s): %s", domain, err)
            return err
