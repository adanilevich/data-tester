"""Testruns page — route: /{domain}/testruns"""

import json

from nicegui import background_tasks, ui

from src.client_interface import TestRunDTO
from src.dtos import Result, Status as RunStatus, TestCaseDTO, TestType
from src.ui.client import DataTesterClient
from src.ui.common import Status as LoadStatus
from src.ui.components import NavBar, StatusBar, render_testobject_matrix
from src.ui.controller import Controller, NiceGuiState

_STATUS_BADGE: dict[RunStatus, tuple[str, str]] = {
    RunStatus.FINISHED: ("bg-teal-900", "text-teal-400"),
    RunStatus.ERROR: ("bg-red-900", "text-red-400"),
    RunStatus.EXECUTING: ("bg-yellow-900", "text-yellow-400"),
    RunStatus.PRECONDITIONS: ("bg-yellow-900", "text-yellow-400"),
    RunStatus.INITIATED: ("bg-slate-700", "text-slate-400"),
    RunStatus.ABORTED: ("bg-orange-900", "text-orange-400"),
    RunStatus.NOT_STARTED: ("bg-slate-800", "text-slate-600"),
}

_RESULT_STYLE: dict[Result, str] = {
    Result.OK: "color: #2dd4bf; cursor: pointer; font-size: 0.7rem;",
    Result.NOK: "color: #f87171; cursor: pointer; font-size: 0.7rem;",
    Result.NA: "color: #fbbf24; cursor: pointer; font-size: 0.7rem;",
}

_RESULT_COLOR: dict[Result, str] = {
    Result.OK: "#2dd4bf",
    Result.NOK: "#f87171",
    Result.NA: "#fbbf24",
}

_RESULT_ICON: dict[Result, str] = {
    Result.OK: "check_circle",
    Result.NOK: "cancel",
    Result.NA: "help",
}


def _render_kv_table(rows: list[tuple[str, str]]) -> None:
    """Render a compact key/value table with monospace dark-theme styling."""
    with ui.element("table").style(
        "width: 100%; border-collapse: collapse; "
        "font-family: monospace; font-size: 0.7rem;"
    ):
        for key, value in rows:
            with ui.element("tr"):
                with ui.element("td").style(
                    "padding: 2px 8px 2px 0; color: #64748b; "
                    "white-space: nowrap; vertical-align: top;"
                ):
                    ui.label(key)
                with ui.element("td").style("padding: 2px 0; color: #94a3b8;"):
                    ui.label(value)


def _show_testcase_dialog(tc: TestCaseDTO) -> None:
    with (
        ui.dialog() as dlg,
        ui.card().style(
            "width: 700px; height: 80vh; display: flex; flex-direction: column; "
            "background: #161b27; border: 1px solid #334155;"
        ),
    ):
        with ui.element("div").style("flex: 1; overflow-y: auto; padding: 1rem;"):
            # 1. Header row
            with ui.row().classes("items-center w-full").style("gap: 0.75rem;"):
                ui.label(tc.testobject.name).style(
                    "font-family: monospace; font-weight: 700; "
                    "color: #f1f5f9; font-size: 0.85rem;"
                )
                with ui.element("div").classes(
                    "bg-slate-700 text-slate-300 text-xs font-mono px-2 py-0.5 rounded"
                ):
                    ui.label(tc.testtype.value)

                result_color = _RESULT_COLOR.get(tc.result, "#94a3b8")
                with ui.element("div").style(
                    f"background: #1e293b; color: {result_color}; "
                    "font-size: 0.7rem; font-family: monospace; "
                    "padding: 0.125rem 0.5rem; border-radius: 0.25rem;"
                ):
                    ui.label(tc.result.value)

                bg, fg = _STATUS_BADGE.get(tc.status, ("bg-slate-700", "text-slate-400"))
                with ui.element("div").classes(
                    f"{bg} {fg} text-xs font-mono px-2 py-0.5 rounded"
                ):
                    ui.label(tc.status.value)

            ui.separator().style("background: #1e293b; margin: 0.75rem 0;")

            # 2. Summary
            ui.label("Summary").classes("text-slate-500 text-xs font-mono font-bold")
            ui.label(tc.summary).classes("text-slate-300 text-xs font-mono")

            ui.separator().style("background: #1e293b; margin: 0.75rem 0;")

            # 3. Metadata table
            ui.label("Metadata").classes("text-slate-500 text-xs font-mono font-bold")
            meta_rows: list[tuple[str, str]] = [
                ("id", str(tc.id)),
                ("testrun_id", str(tc.testrun_id)),
                ("testset_name", tc.testset_name),
                ("domain", tc.domain),
                ("stage", tc.stage),
                ("instance", tc.instance),
                ("started", tc.start_ts.strftime("%Y-%m-%d %H:%M:%S")),
                (
                    "ended",
                    tc.end_ts.strftime("%Y-%m-%d %H:%M:%S") if tc.end_ts else "\u2014",
                ),
            ]
            if tc.scenario:
                meta_rows.append(("scenario", tc.scenario))
            if tc.labels:
                meta_rows.append(("labels", ", ".join(tc.labels)))
            _render_kv_table(meta_rows)

            # 4. Specs
            if tc.specs:
                ui.separator().style("background: #1e293b; margin: 0.75rem 0;")
                ui.label("Specs").classes("text-slate-500 text-xs font-mono font-bold")
                seen_spec_types: set[str] = set()
                for spec in tc.specs:
                    spec_type_val = spec.spec_type.value
                    if spec_type_val in seen_spec_types:
                        continue
                    seen_spec_types.add(spec_type_val)
                    href = (
                        f"/{tc.domain}/specs"
                        f"?stage={tc.stage}"
                        f"&testobject={tc.testobject.name}"
                        f"&spectype={spec_type_val}"
                    )
                    with ui.row().classes("items-center").style("gap: 0.5rem;"):
                        ui.label(spec_type_val).style(
                            "font-family: monospace; font-size: 0.7rem; color: #94a3b8;"
                        )
                        ui.link("view", href, new_tab=True).style(
                            "color: #2dd4bf; font-family: monospace; font-size: 0.7rem;"
                        )

            # 5. Expandable: Diff
            if tc.diff:
                ui.separator().style("background: #1e293b; margin: 0.75rem 0;")
                with (
                    ui.expansion("Diff")
                    .classes("w-full")
                    .style(
                        "color: #94a3b8; font-family: monospace; font-size: 0.75rem;"
                    )
                    .props("dark dense")
                ):
                    ui.code(
                        json.dumps(tc.diff, indent=2, default=str), language="json"
                    ).classes("w-full text-xs")

            # 6. Expandable: Facts
            if tc.facts:
                ui.separator().style("background: #1e293b; margin: 0.75rem 0;")
                with (
                    ui.expansion("Facts")
                    .classes("w-full")
                    .style(
                        "color: #94a3b8; font-family: monospace; font-size: 0.75rem;"
                    )
                    .props("dark dense")
                ):
                    _render_kv_table(
                        [(str(k), str(v)) for fact in tc.facts for k, v in fact.items()]
                    )

            # 7. Expandable: Details
            if tc.details:
                ui.separator().style("background: #1e293b; margin: 0.75rem 0;")
                with (
                    ui.expansion("Details")
                    .classes("w-full")
                    .style(
                        "color: #94a3b8; font-family: monospace; font-size: 0.75rem;"
                    )
                    .props("dark dense")
                ):
                    headers = list(tc.details[0].keys())
                    with ui.element("div").style("overflow-x: auto;"):
                        with ui.element("table").style(
                            "width: 100%; border-collapse: collapse; "
                            "font-family: monospace; font-size: 0.65rem;"
                        ):
                            with ui.element("thead"):
                                with ui.element("tr"):
                                    for h in headers:
                                        with ui.element("th").style(
                                            "text-align: left; padding: 3px 8px; "
                                            "color: #64748b; font-weight: 600; "
                                            "border-bottom: 1px solid #1e293b; "
                                            "white-space: nowrap;"
                                        ):
                                            ui.label(str(h))
                            with ui.element("tbody"):
                                for row in tc.details:
                                    with ui.element("tr").style(
                                        "border-bottom: 1px solid #0f172a;"
                                    ):
                                        for h in headers:
                                            with ui.element("td").style(
                                                "padding: 3px 8px; color: #94a3b8; "
                                                "white-space: nowrap;"
                                            ):
                                                ui.label(str(row.get(h, "")))

        # Sticky bottom action bar — Close only
        with ui.element("div").style(
            "border-top: 1px solid #334155; padding: 0.75rem 1rem;"
        ):
            with ui.row().classes("items-center justify-end").style("gap: 0.5rem;"):
                ui.button("Close", on_click=dlg.close).props("flat dense").classes(
                    "text-slate-400 font-mono text-xs"
                )

    dlg.open()


def _render_result_matrix(testrun: TestRunDTO) -> None:
    columns: list[TestType] = sorted(
        {tc.testtype for tc in testrun.results}, key=lambda t: t.value
    )
    rows: list[str] = sorted({tc.testobject.name for tc in testrun.results})

    if not rows or not columns:
        ui.label("No test results available.").classes("text-slate-500 text-xs font-mono")
        return

    cell_map = {(tc.testobject.name, tc.testtype): tc for tc in testrun.results}

    def cell_fn(obj: str, tt: TestType) -> None:
        if (obj, tt) in cell_map:
            tc = cell_map[(obj, tt)]
            ui.label(tc.result.value).style(_RESULT_STYLE[tc.result]).on(
                "click", lambda _, tc=tc: _show_testcase_dialog(tc)
            )
        else:
            ui.label("—").style("color: #475569; font-size: 0.7rem;")

    render_testobject_matrix(rows, columns, cell_fn)


def _render_testrun_card(testrun: TestRunDTO) -> None:
    expanded = {"open": False}

    with (
        ui.card()
        .classes("w-full bg-[#161b27] border border-slate-700 rounded-lg p-0")
        .props("flat")
    ):
        with ui.row().classes("w-full items-center px-4 py-2").style("gap: 0.75rem;"):
            toggle_btn = (
                ui.button(icon="expand_more")
                .props("flat dense round")
                .classes("text-slate-400")
            )
            _, fg = _STATUS_BADGE.get(testrun.status, ("bg-slate-700", "text-slate-400"))
            with ui.icon("circle", size="xs").classes(fg):
                ui.tooltip(testrun.status.value)
            result_color = _RESULT_COLOR.get(testrun.result, "#94a3b8")
            with ui.icon(
                _RESULT_ICON.get(testrun.result, "help"), size="xs"
            ).style(f"color: {result_color};"):
                ui.tooltip(testrun.result.value)
            with ui.element("div").classes("flex flex-col flex-1"):
                ui.label(testrun.testset_name).classes(
                    "font-bold text-white text-sm font-mono"
                )
                ui.label(testrun.start_ts.strftime("%Y-%m-%d %H:%M:%S")).classes(
                    "text-slate-500 text-xs font-mono"
                )

            ui.label(f"Stage: {testrun.stage}").classes(
                "text-slate-400 text-xs font-mono"
            )
            ui.label(f"Instance: {testrun.instance}").classes(
                "text-slate-400 text-xs font-mono"
            )

            with ui.element("div").classes(
                "bg-slate-700 text-teal-400 text-xs font-mono px-2 py-0.5 rounded"
            ):
                ui.label(f"OK: {testrun.summary.ok_testcases}")
            with ui.element("div").classes(
                "bg-slate-700 text-red-400 text-xs font-mono px-2 py-0.5 rounded"
            ):
                ui.label(f"NOK: {testrun.summary.nok_testcases}")
            with ui.element("div").classes(
                "bg-slate-700 text-amber-400 text-xs font-mono px-2 py-0.5 rounded"
            ):
                ui.label(f"NA: {testrun.summary.na_testcases}")

            ui.button(
                icon="summarize",
                on_click=lambda: ui.notify("Reports not yet implemented", type="info"),
            ).props("flat dense round").classes(
                "text-teal-400 hover:text-teal-300 transition-colors duration-150"
            )

        body = ui.element("div").classes("px-4 pb-3 w-full")
        with body:
            _render_result_matrix(testrun)
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
    @ui.page("/{domain}/testruns")
    async def testruns_page(domain: str) -> None:
        controller = Controller(client=client, state=NiceGuiState())
        NavBar(controller).render()
        StatusBar(controller, domain).render()

        with (
            ui.column()
            .classes("w-full min-h-screen bg-[#0f1117] px-6 py-6")
            .style("row-gap: 1rem;")
        ):
            ui.label("Testruns").classes(
                "text-white font-mono font-bold text-xl tracking-widest"
            )

            def _get_stages() -> list[str]:
                return sorted({tr.stage for tr in controller.testruns(domain)})

            def _get_instances(stage: str | None = None) -> list[str]:
                runs = controller.testruns(domain)
                if stage:
                    return sorted({tr.instance for tr in runs if tr.stage == stage})
                return sorted({tr.instance for tr in runs})

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
                result_select = (
                    ui.select(
                        options=[
                            "All",
                            Result.OK.value,
                            Result.NOK.value,
                            Result.NA.value,
                        ],
                        value="All",
                        label="Result",
                    )
                    .classes("font-mono w-40")
                    .props("dark outlined dense color=teal-4")
                )
                status_select = (
                    ui.select(
                        options=["All"] + [s.value for s in RunStatus],
                        value="All",
                        label="Status",
                    )
                    .classes("font-mono w-44")
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
                    status_select.value = "All"
                    status_select.update()
                    testrun_list.refresh()

                ui.button(icon="refresh", on_click=_on_refresh).props(
                    "flat dense round"
                ).classes(
                    "text-slate-400 hover:text-teal-400 transition-colors duration-150"
                )

            @ui.refreshable
            def testrun_list() -> None:
                raw_stage = stage_select.value
                raw_instance = instance_select.value
                raw_result = result_select.value
                raw_status = status_select.value
                search = str(search_input.value or "").strip().lower()
                stage: str | None = None if raw_stage == "All" else str(raw_stage)
                instance: str | None = (
                    None if raw_instance == "All" else str(raw_instance)
                )
                result: Result | None = (
                    None if raw_result == "All" else Result(raw_result)
                )
                run_status: RunStatus | None = (
                    None if raw_status == "All" else RunStatus(raw_status)
                )

                all_tr = controller.testruns(domain)
                filtered: list[TestRunDTO] = []
                for tr in all_tr:
                    if stage and tr.stage != stage:
                        continue
                    if instance and tr.instance != instance:
                        continue
                    if result and tr.result != result:
                        continue
                    if run_status and tr.status != run_status:
                        continue
                    if search and not any(
                        search in tc.testobject.name.lower() for tc in tr.results
                    ):
                        continue
                    filtered.append(tr)

                filtered = sorted(filtered, key=lambda tr: tr.start_ts, reverse=True)

                if not filtered:
                    load_status = controller.get_testruns_status(domain)
                    if load_status == LoadStatus.LOADED:
                        msg = (
                            "No testruns found."
                            if not all_tr
                            else "No testruns match the current filters."
                        )
                    else:
                        msg = "Loading testruns..."
                    ui.label(msg).classes("text-slate-500 text-sm font-mono mt-4")
                    return

                for tr in filtered:
                    _render_testrun_card(tr)

            testrun_list()

            async def _load() -> None:
                await controller.load_testruns(domain)
                stage_select.options = ["All"] + _get_stages()
                stage_select.update()
                instance_select.options = ["All"] + _get_instances()
                instance_select.update()
                testrun_list.refresh()

            background_tasks.create(_load())

            def _on_stage_change(_: object = None) -> None:
                raw = stage_select.value
                s = None if raw == "All" else str(raw)
                instance_select.options = ["All"] + _get_instances(s)
                instance_select.value = "All"
                instance_select.update()
                testrun_list.refresh()

            stage_select.on("update:model-value", _on_stage_change)
            instance_select.on("update:model-value", lambda _: testrun_list.refresh())
            result_select.on("update:model-value", lambda _: testrun_list.refresh())
            status_select.on("update:model-value", lambda _: testrun_list.refresh())
            search_input.on("update:model-value", lambda _: testrun_list.refresh())
