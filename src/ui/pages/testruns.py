"""Testruns page — route: /{domain}/testruns"""

import json
import logging

from nicegui import background_tasks, ui

from src.dtos import Result, Status as RunStatus, TestCaseDTO, TestRunDTO, TestType
from src.ui.common import Status as LoadStatus
from src.ui.components import NavBar, StatusBar, render_testobject_matrix
from src.ui.controller import ControllerFactory
from src.ui.styles import (
    CARD_HEADER_ROW_CLASSES,
    CARD_ITEM_DATE_CLASSES,
    CARD_ITEM_META_CLASSES,
    CARD_ITEM_TITLE_CLASSES,
    CARD_SURFACE_CLASSES,
    CARD_TITLE_GROUP_CLASSES,
    DIALOG_SEPARATOR_STYLE,
    ICON_BUTTON_PRIMARY_CLASSES,
    ICON_BUTTON_SECONDARY_CLASSES,
    MATRIX_CELL_NA_STYLE,
    PAGE_CONTENT_COLUMN_CLASSES,
    SELECT_INPUT_PROPS,
    TABLE_HEADER_BORDER_STYLE,
    TABLE_ROW_BORDER_STYLE,
)

_log = logging.getLogger("datatester")

_TERMINAL_STATUSES: frozenset[RunStatus] = frozenset(
    {RunStatus.FINISHED, RunStatus.ERROR, RunStatus.ABORTED}
)

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
    try:
        _render_testcase_dialog(tc)
    except Exception as exc:
        _log.error("Failed to render testcase dialog: %s", exc)
        ui.notify("Could not display test case details.", type="negative")


def _render_testcase_dialog(tc: TestCaseDTO) -> None:
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

            ui.separator().style(DIALOG_SEPARATOR_STYLE)

            # 2. Summary
            ui.label("Summary").classes("text-slate-500 text-xs font-mono font-bold")
            ui.label(tc.summary).classes("text-slate-300 text-xs font-mono")

            ui.separator().style(DIALOG_SEPARATOR_STYLE)

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
                ui.separator().style(DIALOG_SEPARATOR_STYLE)
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
                ui.separator().style(DIALOG_SEPARATOR_STYLE)
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
                ui.separator().style(DIALOG_SEPARATOR_STYLE)
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
                ui.separator().style(DIALOG_SEPARATOR_STYLE)
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
                                            "white-space: nowrap;"
                                        ).style(TABLE_HEADER_BORDER_STYLE):
                                            ui.label(str(h))
                            with ui.element("tbody"):
                                for row in tc.details:
                                    with ui.element("tr").style(TABLE_ROW_BORDER_STYLE):
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
        ui.label("No test results available.").classes(
            "text-slate-500 text-xs font-mono"
        )
        return

    cell_map = {(tc.testobject.name, tc.testtype): tc for tc in testrun.results}

    def cell_fn(obj: str, tt: TestType) -> None:
        if (obj, tt) in cell_map:
            tc = cell_map[(obj, tt)]
            ui.label(tc.result.value).style(_RESULT_STYLE[tc.result]).on(
                "click", lambda _, tc=tc: _show_testcase_dialog(tc)
            )
        else:
            ui.label("—").style(MATRIX_CELL_NA_STYLE)

    render_testobject_matrix(rows, columns, cell_fn)


def _render_testrun_card(testrun: TestRunDTO) -> None:
    expanded = {"open": False}

    with ui.card().classes(CARD_SURFACE_CLASSES).props("flat"):
        with ui.row().classes(CARD_HEADER_ROW_CLASSES).style("gap: 0.75rem;"):
            toggle_btn = (
                ui.button(icon="expand_more")
                .props("flat dense round")
                .classes("text-slate-400")
            )
            with ui.row().classes(CARD_TITLE_GROUP_CLASSES).style("gap: 0.4rem;"):
                _, fg = _STATUS_BADGE.get(
                    testrun.status, ("bg-slate-700", "text-slate-400")
                )
                with ui.icon("circle", size="xs").classes(fg):
                    ui.tooltip(testrun.status.value)
                result_color = _RESULT_COLOR.get(testrun.result, "#94a3b8")
                with ui.icon(
                    _RESULT_ICON.get(testrun.result, "help"), size="xs"
                ).style(f"color: {result_color};"):
                    ui.tooltip(testrun.result.value)
                with ui.element("div").classes("flex flex-col"):
                    ui.label(testrun.testset_name).classes(CARD_ITEM_TITLE_CLASSES)
                    ui.label(
                        f"started: {testrun.start_ts.strftime('%Y-%m-%d %H:%M:%S')}"
                    ).classes(CARD_ITEM_DATE_CLASSES)
                    if testrun.end_ts and testrun.status in _TERMINAL_STATUSES:
                        ui.label(
                            f"ended:   {testrun.end_ts.strftime('%Y-%m-%d %H:%M:%S')}"
                        ).classes(CARD_ITEM_DATE_CLASSES)

            ui.label(f"Stage: {testrun.stage}").classes(CARD_ITEM_META_CLASSES)
            ui.label(f"Instance: {testrun.instance}").classes(CARD_ITEM_META_CLASSES)

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
            ).props("flat dense round").classes(ICON_BUTTON_PRIMARY_CLASSES)

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


def register(make_controller: ControllerFactory) -> None:
    @ui.page("/{domain}/testruns")
    async def testruns_page(domain: str) -> None:
        controller = make_controller()
        known = controller.state.domains
        if known and domain not in known:
            ui.navigate.to("/")
            return
        NavBar(controller).render()
        StatusBar(controller, domain).render()

        with (
            ui.column()
            .classes(PAGE_CONTENT_COLUMN_CLASSES)
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
                    .props(SELECT_INPUT_PROPS)
                )
                instance_select = (
                    ui.select(
                        options=["All"] + _get_instances(),
                        value="All",
                        label="Instance",
                    )
                    .classes("font-mono w-40")
                    .props(SELECT_INPUT_PROPS)
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
                    .props(SELECT_INPUT_PROPS)
                )
                status_select = (
                    ui.select(
                        options=["All"] + [s.value for s in RunStatus],
                        value="All",
                        label="Status",
                    )
                    .classes("font-mono w-44")
                    .props(SELECT_INPUT_PROPS)
                )
                search_input = (
                    ui.input(placeholder="Search testobject...")
                    .classes("font-mono flex-1")
                    .props("dark outlined dense clearable")
                )

                async def _on_refresh() -> None:
                    await controller.load_backend_data(domain, force=True)
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
                ).classes(ICON_BUTTON_SECONDARY_CLASSES)

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

            async def _load_and_start_polling() -> None:
                await controller.load_testruns(domain, force=True)
                stage_select.options = ["All"] + _get_stages()
                stage_select.update()
                instance_select.options = ["All"] + _get_instances()
                instance_select.update()
                testrun_list.refresh()
                # Activate polling if preliminary items already exist after initial load
                if controller.state.preliminary_testruns(domain):
                    poll_timer.activate()

            async def _poll() -> None:
                await controller.load_testruns(domain, force=True)
                testrun_list.refresh()
                if not controller.state.preliminary_testruns(domain):
                    poll_timer.deactivate()

            poll_timer = ui.timer(5.0, _poll, active=False)

            async def _bg_refresh() -> None:
                """Periodic background reload — TTL guards prevent over-fetching."""
                await controller.load_testruns(domain)
                testrun_list.refresh()

            bg_timer = ui.timer(5.0, _bg_refresh)
            ui.context.client.on_disconnect(lambda: bg_timer.cancel())

            background_tasks.create_lazy(
                _load_and_start_polling(), name=f"load_testruns_{domain}"
            )

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
