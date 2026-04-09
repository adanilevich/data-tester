"""Testsets page — route: /{domain}/testsets"""

from typing import Any, Callable
from uuid import UUID

from nicegui import background_tasks, ui

from src.dtos import DomainConfigDTO, TestCaseEntryDTO, TestSetDTO, TestType
from src.ui.common import IGNORED_TESTTYPES
from src.ui.components import NavBar, StatusBar, render_testobject_matrix
from src.ui.controller import ControllerFactory
from src.ui.styles import (
    CARD_HEADER_ROW_CLASSES,
    CARD_ITEM_DATE_CLASSES,
    CARD_ITEM_META_CLASSES,
    CARD_ITEM_TITLE_CLASSES,
    CARD_SURFACE_CLASSES,
    CARD_TITLE_GROUP_CLASSES,
    ICON_BUTTON_PRIMARY_CLASSES,
    ICON_BUTTON_SECONDARY_CLASSES,
    MATRIX_CELL_NA_STYLE,
    PAGE_CONTENT_COLUMN_CLASSES,
    SELECT_INPUT_PROPS,
)

_APPLICABLE_TESTTYPES: set[TestType] = set(TestType) - IGNORED_TESTTYPES
_STAGE_NA: set[TestType] = {TestType.ROWCOUNT, TestType.COMPARE}
_NON_STAGE_NA: set[TestType] = {TestType.STAGECOUNT}


def _applicable_for(testobject: str) -> set[TestType]:
    """Applicable test types for a testobject based on its naming convention."""
    if testobject.startswith("raw_"):
        return set()
    if testobject.startswith("stage_"):
        return _APPLICABLE_TESTTYPES - _STAGE_NA
    return _APPLICABLE_TESTTYPES - _NON_STAGE_NA


def _matrix_columns(testset: TestSetDTO) -> list[TestType]:
    """Columns = union of applicable types for all testobjects + any present types."""
    cols: set[TestType] = set()
    for tc in testset.testcases.values():
        cols |= _applicable_for(tc.testobject)
    cols |= {tc.testtype for tc in testset.testcases.values()} - IGNORED_TESTTYPES
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
            with ui.label("—").style(MATRIX_CELL_NA_STYLE):
                ui.tooltip("Testcase is not applicable to the test object")

    render_testobject_matrix(testobjects, testtypes, cell_fn)


def _render_testset_card(
    testset: TestSetDTO,
    on_run: Callable[[], object],
    on_edit: Callable[[], object],
    on_delete: Callable[[], object],
) -> None:
    count = len(testset.testcases)
    expanded = {"open": False}

    with ui.card().classes(CARD_SURFACE_CLASSES).props("flat"):
        with ui.row().classes(CARD_HEADER_ROW_CLASSES).style("gap: 0.75rem;"):
            toggle_btn = (
                ui.button(icon="expand_more")
                .props("flat dense round")
                .classes("text-slate-400")
            )
            with ui.row().classes(CARD_TITLE_GROUP_CLASSES).style("gap: 0.4rem;"):
                with ui.icon("info_outline", size="xs").classes(
                    "text-teal-400 cursor-default"
                    if testset.description
                    else "text-slate-600 cursor-default opacity-40"
                ):
                    ui.tooltip(
                        testset.description if testset.description else "No description"
                    ).classes("text-base")
                with ui.icon("comment", size="xs").classes(
                    "text-amber-500 cursor-default"
                    if testset.comment
                    else "text-slate-600 cursor-default opacity-40"
                ):
                    ui.tooltip(
                        testset.comment if testset.comment else "No comment"
                    ).classes("text-base")
                with ui.element("div").classes("flex flex-col"):
                    ui.label(testset.name).classes(CARD_ITEM_TITLE_CLASSES)
                    ui.label(testset.modified_at.strftime("%Y-%m-%d %H:%M:%S")).classes(
                        CARD_ITEM_DATE_CLASSES
                    )
            ui.label(f"Stage: {testset.default_stage}").classes(CARD_ITEM_META_CLASSES)
            ui.label(f"Instance: {testset.default_instance}").classes(
                CARD_ITEM_META_CLASSES
            )
            with ui.element("div").classes(
                "bg-slate-700 text-teal-400 text-xs font-mono px-2 py-0.5 rounded"
            ):
                ui.label(f"{count} testcases")
            ui.button(
                icon="delete",
                on_click=on_delete,
            ).props("flat dense round").classes(ICON_BUTTON_SECONDARY_CLASSES)
            ui.button(
                icon="edit",
                on_click=on_edit,
            ).props("flat dense round").classes(ICON_BUTTON_SECONDARY_CLASSES)
            ui.button(
                icon="play_arrow",
                on_click=on_run,
            ).props("flat dense round").classes(ICON_BUTTON_PRIMARY_CLASSES)

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


def register(make_controller: ControllerFactory) -> None:
    """Register the testsets page route."""

    @ui.page("/{domain}/testsets")
    async def testsets_page(domain: str) -> None:
        controller = make_controller()
        known = controller.state.domains
        if known and domain not in known:
            ui.navigate.to("/")
            return
        NavBar(controller).render()
        StatusBar(controller, domain).render()
        background_tasks.create_lazy(
            controller.load_backend_data(domain), name=f"load_{domain}"
        )

        with ui.column().classes(PAGE_CONTENT_COLUMN_CLASSES).style("row-gap: 1rem;"):
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
                    testset_list.refresh()

                ui.button(icon="add", on_click=lambda: _open_new_dialog()).props(
                    "flat dense round"
                ).classes(ICON_BUTTON_SECONDARY_CLASSES)

                ui.button(icon="refresh", on_click=_on_refresh).props(
                    "flat dense round"
                ).classes(ICON_BUTTON_SECONDARY_CLASSES)

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

                async def _run_testset(ts: TestSetDTO) -> None:
                    with (
                        ui.dialog() as dlg,
                        ui.card()
                        .props("dark")
                        .classes("bg-[#161b27] border border-slate-700"),
                    ):
                        ui.label(f"Start testrun for '{ts.name}'?").classes(
                            "font-mono text-sm text-slate-200 mb-1"
                        )
                        ui.label(
                            f"Stage: {ts.stage}  ·  Instance: {ts.instance}"
                        ).classes("font-mono text-xs text-slate-400 mb-4")
                        with ui.row().classes("items-center justify-end w-full").style(
                            "gap: 0.5rem;"
                        ):
                            ui.button("Cancel", on_click=dlg.close).props(
                                "flat dense"
                            ).classes("text-slate-400 font-mono text-xs")

                            async def _confirm(_: object = None) -> None:
                                dlg.close()
                                _, err = await controller.execute_testrun(domain, ts)
                                if err:
                                    ui.notify(err, type="negative")
                                else:
                                    ui.navigate.to(f"/{domain}/testruns")

                            ui.button("Run", on_click=_confirm).props("dense").classes(
                                "bg-teal-700 text-white font-mono text-xs"
                            )
                    dlg.open()

                async def _confirm_delete(ts: TestSetDTO) -> None:
                    with (
                        ui.dialog() as dlg,
                        ui.card()
                        .props("dark")
                        .classes("bg-[#161b27] border border-slate-700"),
                    ):
                        ui.label(f"Delete '{ts.name}'?").classes(
                            "font-mono text-sm text-slate-200 mb-1"
                        )
                        ui.label("This cannot be undone.").classes(
                            "font-mono text-xs text-red-400 mb-4"
                        )
                        with ui.row().classes("items-center justify-end w-full").style(
                            "gap: 0.5rem;"
                        ):
                            ui.button("Cancel", on_click=dlg.close).props(
                                "flat dense"
                            ).classes("text-slate-400 font-mono text-xs")

                            async def _confirm(_: object = None) -> None:
                                dlg.close()
                                err = await controller.delete_testset(
                                    domain, str(ts.testset_id)
                                )
                                if err:
                                    ui.notify(err, type="negative")
                                else:
                                    testset_list.refresh()

                            ui.button("Delete", on_click=_confirm).props("dense").classes(
                                "bg-red-700 text-white font-mono text-xs"
                            )
                    dlg.open()

                for ts in filtered:

                    async def _on_run(ts: TestSetDTO = ts) -> None:
                        await _run_testset(ts)

                    def _on_edit(ts: TestSetDTO = ts) -> None:
                        _open_edit_dialog(ts)

                    async def _on_delete(ts: TestSetDTO = ts) -> None:
                        await _confirm_delete(ts)

                    _render_testset_card(
                        ts, on_run=_on_run, on_edit=_on_edit, on_delete=_on_delete
                    )

            testset_list()

            # New/edit dialog — constructed once at page scope, outside refreshable
            selected: dict[tuple[str, TestType], bool] = {}
            edit_testset_id: dict[str, str | None] = {"value": None}

            with ui.dialog() as new_testset_dialog, ui.card().props("dark").classes(
                "bg-[#161b27] border border-slate-700"
            ).style("min-width: 700px; max-width: 90vw;"):
                dialog_title = ui.label("New Testset").classes(
                    "text-white font-mono font-bold text-base tracking-widest mb-2"
                )

                name_input = (
                    ui.input(label="Name", placeholder="Testset name")
                    .classes("font-mono w-full")
                    .props("dark outlined dense")
                )
                description_input = (
                    ui.input(label="Description", placeholder="Optional description")
                    .classes("font-mono w-full")
                    .props("dark outlined dense")
                )
                comment_input = (
                    ui.input(label="Comment", placeholder="Optional comment")
                    .classes("font-mono w-full")
                    .props("dark outlined dense")
                )

                with ui.row().classes("w-full items-center").style("gap: 0.75rem;"):
                    dialog_stage_select = (
                        ui.select(
                            options=_get_stages(),
                            value=_get_stages()[0] if _get_stages() else "",
                            label="Stage",
                        )
                        .classes("font-mono w-40")
                        .props(SELECT_INPUT_PROPS)
                    )
                    dialog_instance_select = (
                        ui.select(
                            options=_get_instances(
                                _get_stages()[0] if _get_stages() else None
                            ),
                            value=(
                                _get_instances(
                                    _get_stages()[0] if _get_stages() else None
                                )[0]
                                if _get_instances(
                                    _get_stages()[0] if _get_stages() else None
                                )
                                else ""
                            ),
                            label="Instance",
                        )
                        .classes("font-mono w-40")
                        .props(SELECT_INPUT_PROPS)
                    )

                @ui.refreshable
                def matrix_view() -> None:
                    current_stage = str(dialog_stage_select.value or "")
                    all_objects = controller.testobjects(domain)
                    stage_objects = [
                        o for o in all_objects if o.stage == current_stage
                    ]
                    obj_names = sorted(
                        {o.name for o in stage_objects if _applicable_for(o.name)}
                    )

                    if not obj_names:
                        ui.label("No testobjects for this stage.").classes(
                            "text-slate-500 text-xs font-mono"
                        )
                        return

                    col_set: set[TestType] = set()
                    for obj_name in obj_names:
                        col_set |= _applicable_for(obj_name)
                    cols = sorted(col_set, key=lambda t: t.value)

                    def cell_fn(obj_name: str, tt: TestType) -> None:
                        if tt in _applicable_for(obj_name):
                            cb_val = selected.get((obj_name, tt), False)

                            def _on_change(
                                e: Any,
                                o: str = obj_name,
                                t: TestType = tt,
                            ) -> None:
                                selected[(o, t)] = e.value

                            ui.checkbox(value=cb_val, on_change=_on_change).props(
                                "dense dark"
                            ).classes("text-teal-400")
                        else:
                            ui.label("—").style(MATRIX_CELL_NA_STYLE)

                    render_testobject_matrix(obj_names, cols, cell_fn)

                matrix_view()

                def _on_dialog_stage_change(_: object = None) -> None:
                    stage_val = str(dialog_stage_select.value or "")
                    inst_opts = _get_instances(stage_val)
                    dialog_instance_select.options = inst_opts
                    dialog_instance_select.value = inst_opts[0] if inst_opts else ""
                    dialog_instance_select.update()
                    selected.clear()
                    matrix_view.refresh()

                dialog_stage_select.on("update:model-value", _on_dialog_stage_change)

                async def _do_save() -> TestSetDTO | None:
                    name = name_input.value.strip() if name_input.value else ""
                    if not name:
                        ui.notify("Name is required.", type="warning")
                        return None
                    testcases: dict[str, TestCaseEntryDTO] = {}
                    for (obj, tt), v in selected.items():
                        if v:
                            entry = TestCaseEntryDTO(
                                domain=domain, testobject=obj, testtype=tt
                            )
                            testcases[entry.identifier] = entry
                    existing_id = edit_testset_id["value"]
                    if existing_id:
                        ts = TestSetDTO(
                            testset_id=UUID(existing_id),
                            name=name,
                            description=description_input.value or "",
                            comment=comment_input.value or "",
                            domain=domain,
                            default_stage=str(dialog_stage_select.value),
                            default_instance=str(dialog_instance_select.value),
                            testcases=testcases,
                        )
                    else:
                        ts = TestSetDTO(
                            name=name,
                            description=description_input.value or "",
                            comment=comment_input.value or "",
                            domain=domain,
                            default_stage=str(dialog_stage_select.value),
                            default_instance=str(dialog_instance_select.value),
                            testcases=testcases,
                        )
                    err = await controller.save_testset(domain, ts)
                    if err:
                        ui.notify(f"Save failed: {err}", type="negative")
                        return None
                    testset_list.refresh()
                    return ts

                async def _on_save() -> None:
                    ts = await _do_save()
                    if ts:
                        new_testset_dialog.close()

                async def _on_save_and_run() -> None:
                    ts = await _do_save()
                    if ts is None:
                        return
                    new_testset_dialog.close()
                    _, err = await controller.execute_testrun(domain, ts)
                    if err:
                        ui.notify(err, type="negative")
                    else:
                        ui.navigate.to(f"/{domain}/testruns")

                with ui.row().classes("items-center justify-end w-full").style(
                    "gap: 0.5rem; margin-top: 1rem;"
                ):
                    ui.button("Cancel", on_click=new_testset_dialog.close).props(
                        "flat dense"
                    ).classes("text-slate-400 font-mono text-xs")
                    ui.button("Save", on_click=_on_save).props("dense").classes(
                        "bg-slate-700 text-white font-mono text-xs"
                    )
                    ui.button("Save & Run", on_click=_on_save_and_run).props(
                        "dense"
                    ).classes("bg-teal-700 text-white font-mono text-xs")

            def _open_new_dialog() -> None:
                edit_testset_id["value"] = None
                dialog_title.set_text("New Testset")
                selected.clear()
                name_input.value = ""
                description_input.value = ""
                comment_input.value = ""
                stages = _get_stages()
                dialog_stage_select.options = stages
                dialog_stage_select.value = stages[0] if stages else ""
                dialog_stage_select.update()
                inst = _get_instances(dialog_stage_select.value)
                dialog_instance_select.options = inst
                dialog_instance_select.value = inst[0] if inst else ""
                dialog_instance_select.update()
                matrix_view.refresh()
                new_testset_dialog.open()

            def _open_edit_dialog(ts: TestSetDTO) -> None:
                edit_testset_id["value"] = str(ts.testset_id)
                dialog_title.set_text("Edit Testset")
                selected.clear()
                for tc in ts.testcases.values():
                    selected[(tc.testobject, tc.testtype)] = True
                name_input.value = ts.name
                description_input.value = ts.description
                comment_input.value = ts.comment
                stages = _get_stages()
                dialog_stage_select.options = stages
                dialog_stage_select.value = ts.default_stage
                dialog_stage_select.update()
                inst = _get_instances(ts.default_stage)
                dialog_instance_select.options = inst
                dialog_instance_select.value = ts.default_instance
                dialog_instance_select.update()
                matrix_view.refresh()
                new_testset_dialog.open()

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

            async def _bg_refresh() -> None:
                """Periodic background reload — TTL guards prevent over-fetching."""
                await controller.load_backend_data(domain)
                testset_list.refresh()

            bg_timer = ui.timer(5.0, _bg_refresh)
            ui.context.client.on_disconnect(lambda: bg_timer.cancel())
