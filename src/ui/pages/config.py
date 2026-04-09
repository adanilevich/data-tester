"""Config page — route: /{domain}/config"""

import copy
from typing import Any

from nicegui import background_tasks, ui

from src.dtos import DomainConfigDTO, LocationDTO
from src.ui.components import NavBar, StatusBar
from src.ui.controller import ControllerFactory
from src.ui.styles import CARD_SURFACE_PADDED_CLASSES, SELECT_INPUT_PROPS

_SECTION_LABEL = (
    "text-slate-500 text-xs font-mono font-bold uppercase tracking-widest"
)
_CARD_STYLE = CARD_SURFACE_PADDED_CLASSES
_INPUT_PROPS = SELECT_INPUT_PROPS
_CHIP_STYLE = "bg-slate-700 text-teal-400 text-xs font-mono px-2 py-0.5 rounded"


def _render_chip(text: str) -> None:
    with ui.element("div").classes(_CHIP_STYLE):
        ui.label(text)


def _render_remove_chip(text: str, on_remove: Any) -> None:
    with ui.element("div").classes(
        "bg-slate-700 text-teal-400 text-xs font-mono px-2 py-0.5 rounded "
        "flex items-center"
    ).style("gap: 0.25rem"):
        ui.label(text)
        ui.button(icon="close", on_click=on_remove).props(
            "flat dense round"
        ).classes("text-slate-400 hover:text-red-400").style(
            "font-size: 0.65rem; padding: 0;"
            " min-height: unset; height: 1rem; width: 1rem;"
        )


def register(make_controller: ControllerFactory) -> None:
    """Register the config page route."""

    @ui.page("/{domain}/config")
    async def config_page(domain: str) -> None:
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

        # Edit-mode flag — mutable dict so closures share the same reference
        edit_mode: dict[str, bool] = {"value": False}

        with ui.column().classes("w-full min-h-screen bg-[#0f1117] px-6 py-6").style(
            "row-gap: 1.5rem;"
        ):
            # Header row
            with ui.row().classes("w-full items-center justify-between").style(
                "gap: 1rem;"
            ):
                ui.label("Configuration").classes(
                    "text-white font-mono font-bold text-xl tracking-widest"
                )
                action_row = ui.row().classes("items-center").style("gap: 0.5rem;")

            @ui.refreshable
            def config_content() -> None:
                cfg: DomainConfigDTO | None = controller.domain_configs().get(domain)

                if cfg is None:
                    ui.label("Loading configuration...").classes(
                        "text-slate-500 text-sm font-mono"
                    )
                    return

                # Typed working copies — rebuilt from state on each refresh
                instances_work: dict[str, list[str]] = copy.deepcopy(cfg.instances)
                compare_datatypes_work: list[str] = list(cfg.compare_datatypes)
                sample_size_default_work: dict[str, int] = {
                    "value": cfg.sample_size_default
                }
                per_obj_work: dict[str, int] = dict(cfg.sample_size_per_object)
                # Ensure every stage in instances has a spec-location entry
                spec_locs_work: dict[str, list[str]] = {
                    stage: list(cfg.spec_locations.get(stage, []))
                    for stage in instances_work
                }
                reports_location_work: dict[str, str] = {
                    "value": cfg.reports_location.path
                }

                is_edit = edit_mode["value"]

                # Domain (read-only)
                with ui.card().classes(_CARD_STYLE).props("flat"):
                    with ui.column().classes("w-full q-pa-md").style("gap: 0.5rem;"):
                        ui.label("Domain").classes(_SECTION_LABEL)
                        with ui.row().classes("items-center").style("gap: 0.5rem;"):
                            _render_chip(cfg.domain)

                # Stages & Instances
                with ui.card().classes(_CARD_STYLE).props("flat"):
                    with ui.column().classes("w-full q-pa-md").style("gap: 0.75rem;"):
                        ui.label("Stages & Instances").classes(_SECTION_LABEL)

                        @ui.refreshable
                        def instances_section() -> None:
                            for stage, inst_list in instances_work.items():
                                with ui.row().classes("items-center w-full").style(
                                    "gap: 0.5rem;"
                                ):
                                    ui.label(stage).classes(
                                        "text-slate-300 text-xs font-mono w-24"
                                    )
                                    with ui.row().classes(
                                        "flex-1 flex-wrap items-center"
                                    ).style("gap: 0.4rem;"):
                                        for inst in inst_list:
                                            if is_edit:

                                                def _make_remove_inst(
                                                    s: str, i: str
                                                ) -> Any:
                                                    def _remove(
                                                        _: Any = None,
                                                    ) -> None:
                                                        instances_work[s].remove(i)
                                                        instances_section.refresh()

                                                    return _remove

                                                _render_remove_chip(
                                                    inst,
                                                    _make_remove_inst(stage, inst),
                                                )
                                            else:
                                                _render_chip(inst)

                                        if is_edit:
                                            avail_instances = sorted(
                                                {
                                                    obj.instance
                                                    for obj in controller.testobjects(
                                                        domain
                                                    )
                                                    if obj.stage == stage
                                                }
                                            )
                                            inp = (
                                                ui.select(
                                                    options=avail_instances,
                                                    with_input=True,
                                                    label="add instance",
                                                )
                                                .classes("font-mono")
                                                .style("width: 9rem;")
                                                .props(_INPUT_PROPS)
                                                .props("new-value-mode=add-unique")
                                            )

                                            def _make_add_inst(
                                                s: str, inp_ref: ui.select
                                            ) -> Any:
                                                def _add(_: Any = None) -> None:
                                                    val = str(
                                                        inp_ref.value or ""
                                                    ).strip()
                                                    if (
                                                        val
                                                        and val
                                                        not in instances_work[s]
                                                    ):
                                                        instances_work[s].append(val)
                                                        inp_ref.set_value(None)
                                                        instances_section.refresh()

                                                return _add

                                            inp.on(
                                                "keydown.enter",
                                                _make_add_inst(stage, inp),
                                            )
                                            ui.button(
                                                icon="add",
                                                on_click=_make_add_inst(stage, inp),
                                            ).props("flat dense round").classes(
                                                "text-teal-400"
                                            )

                                    if is_edit:

                                        def _make_remove_stage(s: str) -> Any:
                                            def _remove(_: Any = None) -> None:
                                                del instances_work[s]
                                                spec_locs_work.pop(s, None)
                                                instances_section.refresh()
                                                spec_locations_section.refresh()

                                            return _remove

                                        ui.button(
                                            icon="delete",
                                            on_click=_make_remove_stage(stage),
                                        ).props("flat dense round").classes(
                                            "text-red-400"
                                        )

                            if is_edit:
                                with ui.row().classes("items-center").style(
                                    "gap: 0.5rem;"
                                ):
                                    avail_stages = sorted(
                                        {
                                            obj.stage
                                            for obj in controller.testobjects(domain)
                                        }
                                    )
                                    new_stage_inp = (
                                        ui.select(
                                            options=avail_stages,
                                            with_input=True,
                                            label="new stage",
                                        )
                                        .classes("font-mono")
                                        .style("width: 10rem;")
                                        .props(_INPUT_PROPS)
                                        .props("new-value-mode=add-unique")
                                    )

                                    def _add_stage(_: Any = None) -> None:
                                        val = str(new_stage_inp.value or "").strip()
                                        if val and val not in instances_work:
                                            instances_work[val] = []
                                            spec_locs_work[val] = []
                                            new_stage_inp.set_value(None)
                                            instances_section.refresh()
                                            spec_locations_section.refresh()

                                    ui.button(
                                        "Add Stage", icon="add", on_click=_add_stage
                                    ).props("flat dense").classes(
                                        "text-teal-400 text-xs font-mono"
                                    )

                        instances_section()

                # Spec Locations
                with ui.card().classes(_CARD_STYLE).props("flat"):
                    with ui.column().classes("w-full q-pa-md").style("gap: 0.75rem;"):
                        ui.label("Spec Locations").classes(_SECTION_LABEL)

                        @ui.refreshable
                        def spec_locations_section() -> None:
                            for stage, paths in spec_locs_work.items():
                                with ui.row().classes("items-start w-full").style(
                                    "gap: 0.5rem;"
                                ):
                                    ui.label(stage).classes(
                                        "text-slate-300 text-xs font-mono"
                                        " w-24 shrink-0"
                                    )
                                    with ui.column().classes("flex-1").style(
                                        "gap: 0.4rem;"
                                    ):
                                        for idx, path in enumerate(paths):
                                            if is_edit:

                                                def _make_path_change(
                                                    s: str, i: int
                                                ) -> Any:
                                                    def _on_change(e: Any) -> None:
                                                        spec_locs_work[s][i] = str(
                                                            e.value or ""
                                                        )

                                                    return _on_change

                                                def _make_remove_path(
                                                    s: str, i: int
                                                ) -> Any:
                                                    def _remove(
                                                        _: Any = None,
                                                    ) -> None:
                                                        spec_locs_work[s].pop(i)
                                                        spec_locations_section.refresh()

                                                    return _remove

                                                with ui.row().classes(
                                                    "items-center w-full"
                                                ).style("gap: 0.4rem;"):
                                                    ui.input(
                                                        value=path,
                                                        on_change=_make_path_change(
                                                            stage, idx
                                                        ),
                                                    ).classes("font-mono flex-1").props(
                                                        _INPUT_PROPS
                                                    )
                                                    ui.button(
                                                        icon="remove_circle_outline",
                                                        on_click=_make_remove_path(
                                                            stage, idx
                                                        ),
                                                    ).props("flat dense round").classes(
                                                        "text-red-400"
                                                    )
                                            else:
                                                ui.label(path).classes(
                                                    "text-slate-400 text-xs font-mono"
                                                )

                                        if is_edit:
                                            new_path_inp = (
                                                ui.input(
                                                    placeholder="new path"
                                                    " (e.g. local:///specs/)"
                                                )
                                                .classes("font-mono w-full")
                                                .props(_INPUT_PROPS)
                                            )

                                            def _make_add_path(
                                                s: str, inp: ui.input
                                            ) -> Any:
                                                def _add(_: Any = None) -> None:
                                                    val = str(inp.value or "").strip()
                                                    if val:
                                                        spec_locs_work[s].append(val)
                                                        inp.value = ""
                                                        spec_locations_section.refresh()

                                                return _add

                                            new_path_inp.on(
                                                "keydown.enter",
                                                _make_add_path(stage, new_path_inp),
                                            )
                                            ui.button(
                                                "Add Path",
                                                icon="add",
                                                on_click=_make_add_path(
                                                    stage, new_path_inp
                                                ),
                                            ).props("flat dense").classes(
                                                "text-teal-400 text-xs font-mono"
                                            )

                        spec_locations_section()

                # Reports Location
                with ui.card().classes(_CARD_STYLE).props("flat"):
                    with ui.column().classes("w-full q-pa-md").style("gap: 0.5rem;"):
                        ui.label("Reports Location").classes(_SECTION_LABEL)
                        if is_edit:

                            def _on_reports_change(e: Any) -> None:
                                reports_location_work["value"] = str(e.value or "")

                            ui.input(
                                value=reports_location_work["value"],
                                on_change=_on_reports_change,
                            ).classes("font-mono w-full").props(_INPUT_PROPS)
                        else:
                            ui.label(reports_location_work["value"]).classes(
                                "text-slate-400 text-xs font-mono"
                            )

                # Compare Datatypes
                with ui.card().classes(_CARD_STYLE).props("flat"):
                    with ui.column().classes("w-full q-pa-md").style("gap: 0.5rem;"):
                        ui.label("Compare Datatypes").classes(_SECTION_LABEL)

                        @ui.refreshable
                        def datatypes_section() -> None:
                            with ui.row().classes("flex-wrap items-center").style(
                                "gap: 0.4rem;"
                            ):
                                for dt in compare_datatypes_work:
                                    if is_edit:

                                        def _make_remove_dt(d: str) -> Any:
                                            def _remove(_: Any = None) -> None:
                                                compare_datatypes_work.remove(d)
                                                datatypes_section.refresh()

                                            return _remove

                                        _render_remove_chip(
                                            dt, _make_remove_dt(dt)
                                        )
                                    else:
                                        _render_chip(dt)

                                if is_edit:
                                    new_dt_inp = (
                                        ui.input(placeholder="datatype")
                                        .classes("font-mono")
                                        .style("width: 8rem;")
                                        .props(_INPUT_PROPS)
                                    )

                                    def _add_dt(_: Any = None) -> None:
                                        val = str(new_dt_inp.value or "").strip()
                                        if val and val not in compare_datatypes_work:
                                            compare_datatypes_work.append(val)
                                            new_dt_inp.value = ""
                                            datatypes_section.refresh()

                                    new_dt_inp.on("keydown.enter", _add_dt)
                                    ui.button(
                                        icon="add", on_click=_add_dt
                                    ).props("flat dense round").classes("text-teal-400")

                        datatypes_section()

                # Sample Size
                with ui.card().classes(_CARD_STYLE).props("flat"):
                    with ui.column().classes("w-full q-pa-md").style("gap: 0.75rem;"):
                        ui.label("Sample Size").classes(_SECTION_LABEL)

                        with ui.row().classes("items-center").style("gap: 0.75rem;"):
                            ui.label("Default").classes(
                                "text-slate-300 text-xs font-mono w-24"
                            )
                            if is_edit:

                                def _on_ss_change(e: Any) -> None:
                                    try:
                                        sample_size_default_work["value"] = int(
                                            e.value or 1
                                        )
                                    except (ValueError, TypeError):
                                        pass

                                ui.number(
                                    value=sample_size_default_work["value"],
                                    min=1,
                                    step=1,
                                    on_change=_on_ss_change,
                                ).classes("font-mono").style("width: 8rem;").props(
                                    _INPUT_PROPS
                                )
                            else:
                                ui.label(
                                    str(sample_size_default_work["value"])
                                ).classes("text-slate-400 text-xs font-mono")

                        @ui.refreshable
                        def per_object_section() -> None:
                            if per_obj_work:
                                with ui.element("table").style(
                                    "width: 100%; border-collapse: collapse; "
                                    "font-family: monospace; font-size: 0.75rem;"
                                ):
                                    with ui.element("thead"):
                                        with ui.element("tr"):
                                            for hdr in ("Testobject", "Sample Size", ""):
                                                with ui.element("th").style(
                                                    "text-align: left; padding: 4px 8px; "
                                                    "color: #64748b; font-size: 0.65rem; "
                                                    "border-bottom: 1px solid #1e293b; "
                                                    "font-weight: 600;"
                                                ):
                                                    ui.label(hdr)
                                    with ui.element("tbody"):
                                        for obj_name, sample in per_obj_work.items():
                                            with ui.element("tr").style(
                                                "border-bottom: 1px solid #0f172a;"
                                            ):
                                                with ui.element("td").style(
                                                    "padding: 4px 8px; color: #94a3b8;"
                                                ):
                                                    ui.label(obj_name)
                                                with ui.element("td").style(
                                                    "padding: 4px 8px;"
                                                ):
                                                    if is_edit:

                                                        def _make_po_change(
                                                            n: str,
                                                        ) -> Any:
                                                            def _ch(e: Any) -> None:
                                                                try:
                                                                    per_obj_work[n] = int(
                                                                        e.value or 1
                                                                    )
                                                                except (
                                                                    ValueError,
                                                                    TypeError,
                                                                ):
                                                                    pass

                                                            return _ch

                                                        ui.number(
                                                            value=sample,
                                                            min=1,
                                                            step=1,
                                                            on_change=_make_po_change(
                                                                obj_name
                                                            ),
                                                        ).style(
                                                            "width: 7rem;"
                                                        ).props(_INPUT_PROPS)
                                                    else:
                                                        ui.label(str(sample)).classes(
                                                            "text-slate-400"
                                                            " text-xs font-mono"
                                                        )
                                                with ui.element("td").style(
                                                    "padding: 4px 8px;"
                                                ):
                                                    if is_edit:

                                                        def _make_remove_po(
                                                            n: str,
                                                        ) -> Any:
                                                            def _rm(
                                                                _: Any = None,
                                                            ) -> None:
                                                                del per_obj_work[n]
                                                                per_object_section.refresh()

                                                            return _rm

                                                        ui.button(
                                                            icon="delete",
                                                            on_click=_make_remove_po(
                                                                obj_name
                                                            ),
                                                        ).props(
                                                            "flat dense round"
                                                        ).classes("text-red-400")
                            elif not is_edit:
                                ui.label("No per-object overrides defined.").classes(
                                    "text-slate-500 text-xs font-mono"
                                )

                            if is_edit:
                                with ui.row().classes("items-center").style(
                                    "gap: 0.5rem;"
                                ):
                                    all_obj_names = sorted(
                                        {
                                            obj.name
                                            for obj in controller.testobjects(domain)
                                        }
                                    )
                                    new_po_name = (
                                        ui.select(
                                            options=all_obj_names,
                                            with_input=True,
                                            label="testobject",
                                        )
                                        .classes("font-mono")
                                        .style("width: 12rem;")
                                        .props(_INPUT_PROPS)
                                    )
                                    new_po_size = (
                                        ui.number(value=100, min=1, step=1)
                                        .style("width: 7rem;")
                                        .props(_INPUT_PROPS)
                                    )

                                    def _add_po(_: Any = None) -> None:
                                        n = str(new_po_name.value or "").strip()
                                        if n:
                                            try:
                                                per_obj_work[n] = int(
                                                    new_po_size.value or 1
                                                )
                                            except (ValueError, TypeError):
                                                per_obj_work[n] = 1
                                            new_po_name.set_value(None)
                                            new_po_size.value = 100
                                            per_object_section.refresh()

                                    ui.button(
                                        "Add Override",
                                        icon="add",
                                        on_click=_add_po,
                                    ).props("flat dense").classes(
                                        "text-teal-400 text-xs font-mono"
                                    )

                        per_object_section()

                # Action buttons — rendered inside refreshable so state is current
                action_row.clear()
                with action_row:
                    if is_edit:

                        async def _save(_: Any = None) -> None:
                            try:
                                reports_loc = LocationDTO(
                                    reports_location_work["value"]
                                )
                            except ValueError as exc:
                                ui.notify(
                                    f"Invalid reports location: {exc}",
                                    type="negative",
                                )
                                return

                            new_dto = DomainConfigDTO(
                                domain=domain,
                                instances=instances_work,
                                compare_datatypes=compare_datatypes_work,
                                sample_size_default=sample_size_default_work["value"],
                                sample_size_per_object=per_obj_work,
                                spec_locations=spec_locs_work,
                                reports_location=reports_loc,
                            )
                            err = await controller.save_config(domain, new_dto)
                            if err:
                                ui.notify(f"Save failed: {err}", type="negative")
                            else:
                                ui.notify("Configuration saved.", type="positive")
                                edit_mode["value"] = False
                                config_content.refresh()

                        def _cancel(_: Any = None) -> None:
                            edit_mode["value"] = False
                            config_content.refresh()

                        ui.button("Cancel", on_click=_cancel).props(
                            "flat dense"
                        ).classes("text-slate-400 font-mono text-xs")
                        ui.button("Save", on_click=_save).classes(
                            "bg-teal-500 text-[#0f1117] font-bold font-mono text-xs"
                        ).props("dense")

                    else:

                        def _edit(_: Any = None) -> None:
                            edit_mode["value"] = True
                            config_content.refresh()

                        ui.button("Edit", icon="edit", on_click=_edit).classes(
                            "bg-slate-700 text-teal-400 font-mono text-xs"
                        ).props("dense")

            config_content()
