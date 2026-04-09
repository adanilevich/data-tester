import logging
from datetime import datetime
from uuid import UUID, uuid4

from src.dtos import (
    DomainConfigDTO,
    FindSpecsDTO,
    Result,
    SpecEntryDTO,
    TestCaseEntryDTO,
    TestObjectDTO,
    TestRunDefDTO,
    TestRunDTO,
    TestSetDTO,
    TestType,
)
from src.dtos import Status as RunStatus
from src.ui.client import BackendError, DataTesterClient
from src.ui.common import Status

from .state import State, StateError

_log = logging.getLogger("datatester")


class Controller:
    def __init__(self, client: DataTesterClient, state: State) -> None:
        self._client: DataTesterClient = client
        self.state: State = state

    @property
    def domain(self) -> str | None:
        return self.state.domain

    @domain.setter
    def domain(self, val: str | None) -> None:
        self.state.domain = val

    @property
    def domains(self) -> list[str]:
        return self.state.domains

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
        loaded = self.state.testruns.get(domain, [])
        preliminary = self.state.preliminary_testruns(domain)
        loaded_ids = {str(tr.id) for tr in loaded}
        extras = [p for p in preliminary if str(p.id) not in loaded_ids]
        return list(loaded) + extras

    def get_testruns_status(self, domain: str) -> Status:
        return self.state.testruns_status.get(domain, Status.UNCLEAR)

    def specs(self, domain: str) -> dict[str, list[SpecEntryDTO]]:
        return self.state.specs(domain)

    def get_specs_status(self, domain: str) -> Status:
        return self.state.specs_status.get(domain, Status.UNCLEAR)

    async def load_domains(self) -> str | None:
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
        self.state.set_testruns_status(domain, Status.LOADING)
        try:
            testruns = await self._client.get_testruns(domain)
            self.state.set_testruns(domain, testruns)
            self.state.set_testruns_status(domain, Status.LOADED)
            # Remove preliminary runs that now have real counterparts
            loaded_ids = {str(tr.id) for tr in testruns}
            for ptr in self.state.preliminary_testruns(domain):
                if str(ptr.id) in loaded_ids:
                    self.state.remove_preliminary_testrun(domain, str(ptr.id))
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
        self.state.set_specs_status(domain, Status.LOADING)
        try:
            domain_config = self.state.domain_configs[domain]
            all_testobjects = self.state.testobjects.get(domain, [])

            stage_instance: dict[str, str] = {}
            stage_testobject_names: dict[str, set[str]] = {}
            for obj in all_testobjects:
                if obj.stage not in stage_instance:
                    stage_instance[obj.stage] = obj.instance
                    stage_testobject_names[obj.stage] = set()
                stage_testobject_names[obj.stage].add(obj.name)

            _IGNORED_TESTTYPES = {
                TestType.ABSTRACT,
                TestType.UNKNOWN,
                TestType.DUMMY_OK,
                TestType.DUMMY_NOK,
                TestType.DUMMY_EXCEPTION,
            }
            _TESTTYPES = [tt for tt in TestType if tt not in _IGNORED_TESTTYPES]

            for stage, instance in stage_instance.items():
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
                request = FindSpecsDTO(testset=testset, domain_config=domain_config)
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

    async def save_testset(self, domain: str, testset: TestSetDTO) -> str | None:
        try:
            await self._client.save_testset(domain, testset)
            existing = list(self.state.testsets.get(domain, []))
            ids = {str(ts.testset_id) for ts in existing}
            if str(testset.testset_id) not in ids:
                existing.append(testset)
            else:
                existing = [
                    testset if str(ts.testset_id) == str(testset.testset_id) else ts
                    for ts in existing
                ]
            self.state.set_testsets(domain, existing)
            return None
        except BackendError as exc:
            return f"Backend error {exc.status_code}: {exc.detail}"
        except Exception as exc:
            return f"Could not reach backend: {exc}"

    def build_testrun_def(
        self, domain: str, testset: TestSetDTO
    ) -> tuple[TestRunDefDTO | None, str | None]:
        specs_by_stage = self.state.specs(domain)
        if not specs_by_stage:
            return None, "Specs not loaded for this domain."
        try:
            domain_config = self.state.domain_config
        except StateError as exc:
            return None, str(exc)
        spec_lookup: dict[str, list] = {}
        for stage_entries in specs_by_stage.values():
            for entry in stage_entries:
                key = f"{entry.testobject_name}_{entry.testtype.value}"
                if entry.scenario:
                    key += f"_{entry.scenario}"
                spec_lookup[key] = entry.specs
        spec_list = [spec_lookup.get(ident, []) for ident in testset.testcases]
        try:
            return TestRunDefDTO.from_testset(testset, spec_list, domain_config), None
        except ValueError as exc:
            return None, str(exc)

    async def execute_testrun(
        self, domain: str, testset: TestSetDTO
    ) -> tuple[UUID | None, str | None]:
        testrun_def, err = self.build_testrun_def(domain, testset)
        if err is not None or testrun_def is None:
            return None, err or "Unknown error building testrun definition."
        try:
            testrun_id = await self._client.execute_testrun(domain, testrun_def)
        except BackendError as exc:
            return None, f"Backend error {exc.status_code}: {exc.detail}"
        except Exception as exc:
            return None, f"Could not reach backend: {exc}"

        preliminary = TestRunDTO(
            id=testrun_id,
            testset_id=testset.testset_id,
            domain=domain,
            stage=testset.stage or testset.default_stage,
            instance=testset.instance or testset.default_instance,
            result=Result.NA,
            status=RunStatus.INITIATED,
            start_ts=datetime.now(),
            testset_name=testset.name,
            labels=testset.labels,
            domain_config=self.state.domain_config,
        )
        self.state.add_preliminary_testrun(domain, preliminary)
        return testrun_id, None
