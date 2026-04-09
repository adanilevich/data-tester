"""Testsets page — route: /{domain}/testsets"""

from nicegui import background_tasks, ui

from src.client_interface import DomainConfigDTO, TestSetDTO
from src.dtos import TestType
from src.ui.client import DataTesterClient
from src.ui.components import NavBar, StatusBar, render_testobject_matrix
from src.ui.controller import Controller, NiceGuiState

_IGNORED_TESTTYPES = {
    TestType.ABSTRACT,
    TestType.UNKNOWN,
    TestType.DUMMY_OK,
    TestType.DUMMY_NOK,
    TestType.DUMMY_EXCEPTION,
}
_APPLICABLE_TESTTYPES: set[TestType] = set(TestType) - _IGNORED_TESTTYPES
_STAGE_NA: set[TestType] = {TestType.ROWCOUNT, TestType.COMPARE}
_NON_STAGE_NA: set[TestType] = {TestType.STAGECOUNT}


def _applicable_for(testobject: str) -> set[TestType]:
    """Applicable test types for a testobject based on its naming convention."""
    if testobject.startswith("stage_"):
        return _APPLICABLE_TESTTYPES - _STAGE_NA
    return _APPLICABLE_TESTTYPES - _NON_STAGE_NA


def _matrix_columns(testset: TestSetDTO) -> list[TestType]:
    """Columns = union of applicable types for all testobjects + any present types."""
    cols: set[TestType] = set()
    for tc in testset.testcases.values():
        cols |= _applicable_for(tc.testobject)
    cols |= {tc.testtype for tc in testset.testcases.values()} - _IGNORED_TESTTYPES
    return sorted(cols, key=lambda t: t.value)


def _sorted_testobjects(testset: TestSetDTO) -> list[str]:
    return sorted({tc.testobject for tc in testset.testcases.values()})


def _render_matrix(testset: TestSetDTO) -> None:
    testobjects = _sorted_testobjects(testset)
    testtypes = _matrix_columns(testset)

    if not testobjects or not testtypes:
        ui.label("No test cases defined.").classes("text-slate-500 text-xs font-mono")
        return

    present = {(tc.testobject, tc.testtype) for tc in testset.testcases.values()}

    def cell_fn(obj: str, tt: TestType) -> None:
        if (obj, tt) in present:
            with ui.icon("check", size="xs").classes("text-teal-400"):
                ui.tooltip("Testcase is present in testset")
        elif tt in _applicable_for(obj):
            with ui.icon("radio_button_unchecked", size="xs").classes(
                "text-amber-400 opacity-60"
            ):
                ui.tooltip("Testcase is missing in testset")
        else:
            with ui.label("—").style("color: #475569; font-size: 0.7rem;"):
                ui.tooltip("Testcase is not applicable to the test object")

    render_testobject_matrix(testobjects, testtypes, cell_fn)


def _render_testset_card(testset: TestSetDTO) -> None:
    """Render a single expandable testset card with manual toggle."""
    count = len(testset.testcases)
    expanded = {"open": False}

    with ui.card().classes(
        "w-full bg-[#161b27] border border-slate-700 rounded-lg p-0"
    ).props("flat"):
        # Header row — always visible
        with ui.row().classes("w-full items-center px-4 py-2").style("gap: 0.75rem;"):
            toggle_btn = (
                ui.button(icon="expand_more")
                .props("flat dense round")
                .classes("text-slate-400")
            )
            with ui.row().classes("items-center flex-1").style("gap: 0.4rem;"):
                if testset.description:
                    with ui.icon("info_outline", size="xs").classes(
                        "text-teal-400 cursor-default"
                    ):
                        ui.tooltip(testset.description).classes("text-base")
                if testset.comment:
                    with ui.icon("comment", size="xs").classes(
                        "text-amber-500 cursor-default"
                    ):
                        ui.tooltip(testset.comment).classes("text-base")
                ui.label(testset.name).classes(
                    "font-bold text-white text-sm font-mono"
                )
            ui.label(f"Stage: {testset.default_stage}").classes(
                "text-slate-400 text-xs font-mono"
            )
            ui.label(f"Instance: {testset.default_instance}").classes(
                "text-slate-400 text-xs font-mono"
            )
            with ui.element("div").classes(
                "bg-slate-700 text-teal-400 text-xs font-mono px-2 py-0.5 rounded"
            ):
                ui.label(f"{count} testcases")
            ui.button(
                icon="play_arrow",
                on_click=lambda: ui.notify(
                    "Executions are not yet possible", type="info"
                ),
            ).props("flat dense round").classes(
                "text-teal-400 hover:text-teal-300 transition-colors duration-150"
            )

        # Matrix body — hidden until toggled
        body = ui.element("div").classes("px-4 pb-3 w-full")
        with body:
            _render_matrix(testset)
        body.set_visibility(False)

        def _toggle(_: object = None) -> None:
            expanded["open"] = not expanded["open"]
            body.set_visibility(expanded["open"])
            toggle_btn.props(
                f"icon={'expand_less' if expanded['open'] else 'expand_more'} "
                "flat dense round"
            )

        toggle_btn.on("click", _toggle)


def register(client: DataTesterClient) -> None:
    """Register the testsets page route."""

    @ui.page("/{domain}/testsets")
    async def testsets_page(domain: str) -> None:
        controller = Controller(client=client, state=NiceGuiState())
        NavBar(controller).render()
        StatusBar(controller, domain).render()
        background_tasks.create_lazy(
            controller.load_backend_data(domain), name=f"load_{domain}"
        )

        with ui.column().classes("w-full min-h-screen bg-[#0f1117] px-6 py-6").style(
            "row-gap: 1rem;"
        ):
            ui.label("Testsets").classes(
                "text-white font-mono font-bold text-xl tracking-widest"
            )

            def _get_config() -> DomainConfigDTO | None:
                return controller.domain_configs().get(domain)

            def _get_stages() -> list[str]:
                cfg = _get_config()
                return sorted(cfg.instances.keys()) if cfg else []

            def _get_instances(stage: str | None = None) -> list[str]:
                cfg = _get_config()
                if cfg is None:
                    return []
                if stage:
                    return sorted(cfg.instances.get(stage, []))
                return sorted({i for insts in cfg.instances.values() for i in insts})

            # Filter row
            with ui.row().classes("items-center w-full").style("gap: 0.75rem;"):
                stage_select = (
                    ui.select(
                        options=["All"] + _get_stages(),
                        value="All",
                        label="Stage",
                    )
                    .classes("font-mono w-40")
                    .props("dark outlined dense color=teal-4")
                )
                instance_select = (
                    ui.select(
                        options=["All"] + _get_instances(),
                        value="All",
                        label="Instance",
                    )
                    .classes("font-mono w-40")
                    .props("dark outlined dense color=teal-4")
                )
                search_input = (
                    ui.input(placeholder="Search testobject...")
                    .classes("font-mono flex-1")
                    .props("dark outlined dense clearable")
                )

                async def _on_refresh() -> None:
                    await controller.load_backend_data(domain)
                    stage_select.options = ["All"] + _get_stages()
                    stage_select.value = "All"
                    stage_select.update()
                    instance_select.options = ["All"] + _get_instances()
                    instance_select.value = "All"
                    instance_select.update()
                    testset_list.refresh()

                ui.button(icon="refresh", on_click=_on_refresh).props(
                    "flat dense round"
                ).classes(
                    "text-slate-400 hover:text-teal-400 transition-colors duration-150"
                )

            @ui.refreshable
            def testset_list() -> None:
                raw_stage = stage_select.value
                raw_instance = instance_select.value
                stage: str | None = None if raw_stage == "All" else str(raw_stage)
                instance: str | None = (
                    None if raw_instance == "All" else str(raw_instance)
                )
                search = str(search_input.value or "").strip().lower()

                all_ts = controller.testsets(domain)

                filtered: list[TestSetDTO] = []
                for ts in all_ts:
                    if stage and ts.default_stage != stage:
                        continue
                    if instance and ts.default_instance != instance:
                        continue
                    if search and not any(
                        search in e.testobject.lower() for e in ts.testcases.values()
                    ):
                        continue
                    filtered.append(ts)

                if not filtered:
                    msg = (
                        "Loading testsets..."
                        if not all_ts
                        else "No testsets match the current filters."
                    )
                    ui.label(msg).classes("text-slate-500 text-sm font-mono mt-4")
                    return

                for ts in filtered:
                    _render_testset_card(ts)

            testset_list()

            def _on_stage_change(_: object = None) -> None:
                raw = stage_select.value
                stage = None if raw == "All" else str(raw)
                instance_select.options = ["All"] + _get_instances(stage)
                instance_select.value = "All"
                instance_select.update()
                testset_list.refresh()

            stage_select.on("update:model-value", _on_stage_change)
            instance_select.on("update:model-value", lambda _: testset_list.refresh())
            search_input.on("update:model-value", lambda _: testset_list.refresh())
