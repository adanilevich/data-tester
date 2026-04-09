"""Specs page — route: /{domain}/specs"""

import logging

from nicegui import background_tasks, ui

from src.dtos import SpecEntryDTO, TestType
from src.dtos.specification_dtos import (
    CompareSpecDTO,
    RowcountSpecDTO,
    SchemaSpecDTO,
    StagecountSpecDTO,
)
from src.ui.components import NavBar, StatusBar
from src.ui.controller import ControllerFactory
from src.ui.styles import (
    CARD_HEADER_ROW_CLASSES,
    CARD_ITEM_DATE_CLASSES,
    CARD_ITEM_META_CLASSES,
    CARD_ITEM_TITLE_CLASSES,
    CARD_SURFACE_CLASSES,
    PAGE_CONTENT_COLUMN_CLASSES,
    SELECT_INPUT_PROPS,
    TABLE_HEADER_BORDER_STYLE,
    TABLE_ROW_BORDER_STYLE,
)

_log = logging.getLogger("datatester")

_SPEC_TESTTYPES = [
    TestType.SCHEMA,
    TestType.ROWCOUNT,
    TestType.COMPARE,
    TestType.STAGECOUNT,
]


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


def _render_spec_content_sql(spec: RowcountSpecDTO | CompareSpecDTO) -> None:
    query = spec.query or ""
    if query:
        ui.code(query, language="sql").classes("w-full text-xs")
    else:
        ui.label("(no query)").classes("text-slate-500 text-xs font-mono")


def _render_spec_content_schema(spec: SchemaSpecDTO) -> None:
    if not spec.columns:
        ui.label("(empty schema)").classes("text-slate-500 text-xs font-mono")
        return
    pks = set(spec.primary_keys or [])
    partitions = set(spec.partition_columns or [])
    clusterings = set(spec.clustering_columns or [])

    with ui.element("table").style(
        "width: 100%; border-collapse: collapse; "
        "font-family: monospace; font-size: 0.7rem;"
    ):
        with ui.element("tr"):
            for header in ["column", "dtype", "pk", "partitioning", "clustering"]:
                with ui.element("th").style(
                    TABLE_HEADER_BORDER_STYLE
                    + " padding: 2px 8px; color: #64748b; text-align: left;"
                ):
                    ui.label(header)
        for col, dtype in spec.columns.items():
            with ui.element("tr").style(TABLE_ROW_BORDER_STYLE):
                for val in [
                    col,
                    dtype,
                    "✓" if col in pks else "",
                    "✓" if col in partitions else "",
                    "✓" if col in clusterings else "",
                ]:
                    with ui.element("td").style("padding: 2px 8px; color: #94a3b8;"):
                        ui.label(val)


def _render_spec_content_stagecount(spec: StagecountSpecDTO) -> None:
    rows = [
        ("raw_file_format", spec.raw_file_format or "—"),
        ("raw_file_encoding", spec.raw_file_encoding or "—"),
        (
            "skip_lines",
            str(spec.skip_lines) if spec.skip_lines is not None else "—",
        ),
    ]
    _render_kv_table(rows)


def _render_spec_content(spec: object) -> None:
    if isinstance(spec, SchemaSpecDTO):
        _render_spec_content_schema(spec)
    elif isinstance(spec, (RowcountSpecDTO, CompareSpecDTO)):
        _render_spec_content_sql(spec)
    elif isinstance(spec, StagecountSpecDTO):
        _render_spec_content_stagecount(spec)
    else:
        ui.label("(unknown spec type)").classes("text-slate-500 text-xs font-mono")


def _show_spec_dialog(stage: str, entry: SpecEntryDTO) -> None:
    try:
        _render_spec_dialog(stage, entry)
    except Exception as exc:
        _log.error("Failed to render spec dialog: %s", exc)
        ui.notify("Could not display spec details.", type="negative")


def _render_spec_dialog(stage: str, entry: SpecEntryDTO) -> None:
    _SPEC_SEP_STYLE = "background: #475569; height: 2px; margin: 1.5rem 0;"

    with (
        ui.dialog() as dlg,
        ui.card().style(
            "width: 750px; height: 80vh; min-width: 400px; min-height: 300px; "
            "display: flex; flex-direction: column; "
            "resize: horizontal; overflow: hidden; "
            "background: #161b27; border: 1px solid #334155;"
        ),
    ):
        with ui.element("div").style("flex: 1; overflow-y: auto; padding: 1rem;"):
            # Header row
            with ui.row().classes("items-center w-full").style("gap: 0.75rem;"):
                ui.label(entry.testobject_name).style(
                    "font-family: monospace; font-weight: 700; "
                    "color: #f1f5f9; font-size: 1rem;"
                )
                with ui.element("div").classes(
                    "bg-slate-700 text-slate-300 text-xs font-mono px-2 py-0.5 rounded"
                ):
                    ui.label(entry.testtype.value)
                with ui.element("div").classes(
                    "bg-teal-900 text-teal-400 text-xs font-mono px-2 py-0.5 rounded"
                ):
                    ui.label(stage)
                if entry.scenario:
                    with ui.element("div").classes(
                        "bg-slate-800 text-slate-400 text-xs font-mono "
                        "px-2 py-0.5 rounded"
                    ):
                        ui.label(entry.scenario)

            ui.separator().style(_SPEC_SEP_STYLE)

            # One section per spec in entry.specs
            for i, spec in enumerate(entry.specs):
                if i > 0:
                    ui.separator().style(_SPEC_SEP_STYLE)
                loc_label = spec.display_name or str(spec.location)
                ui.label(loc_label).style(
                    "font-family: monospace; font-size: 0.8rem; font-weight: 600; "
                    "color: #94a3b8; margin-bottom: 0.75rem; display: block;"
                )
                _render_spec_content(spec)

        # Sticky action bar
        with ui.element("div").style(
            "padding: 0.5rem 1rem; border-top: 1px solid #1e293b;"
        ):
            ui.button("Close", on_click=dlg.close).props("flat dense").classes(
                "text-slate-400"
            )

    dlg.open()


def _render_spec_card(stage: str, entry: SpecEntryDTO) -> None:
    card = ui.card().classes(CARD_SURFACE_CLASSES).style("cursor: pointer;")
    with card:
        with ui.row().classes(CARD_HEADER_ROW_CLASSES):
            ui.label(entry.testobject_name).classes(CARD_ITEM_TITLE_CLASSES)
            ui.label(entry.testtype.value).classes(CARD_ITEM_META_CLASSES)
            ui.label(stage).classes(CARD_ITEM_DATE_CLASSES)
            ui.element("div").classes("flex-1")
            ui.label(f"{len(entry.specs)} file(s)").classes(CARD_ITEM_META_CLASSES)
    card.on("click", lambda _e, s=stage, en=entry: _show_spec_dialog(s, en))


def register(make_controller: ControllerFactory) -> None:
    @ui.page("/{domain}/specs")
    async def specs_page(
        domain: str,
        stage: str = "All",
        testobject: str = "",
        spectype: str = "All",
    ) -> None:
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

        # Resolve initial spectype filter: URL uses SpecType values ("schema"),
        # dropdown uses TestType values ("SCHEMA"). Match case-insensitively.
        initial_spectype = "All"
        if spectype and spectype != "All":
            for tt in _SPEC_TESTTYPES:
                if tt.value.lower() == spectype.lower():
                    initial_spectype = tt.value
                    break

        def _get_stages() -> list[str]:
            cfg = controller.domain_configs().get(domain)
            if cfg:
                return sorted(cfg.instances.keys())
            return sorted(controller.specs(domain).keys())

        with ui.column().classes(PAGE_CONTENT_COLUMN_CLASSES):
            ui.label("Specs").style(
                "font-family: monospace; font-weight: 700; "
                "color: #f1f5f9; font-size: 1.1rem; margin-bottom: 0.5rem;"
            )

            with ui.row().classes("items-center w-full").style("gap: 0.75rem;"):
                stage_select = (
                    ui.select(
                        options=["All"] + _get_stages(),
                        value=stage,
                        label="Stage",
                    )
                    .props(SELECT_INPUT_PROPS)
                    .style("min-width: 140px;")
                )
                testobject_input = (
                    ui.input(placeholder="Search testobject...", value=testobject)
                    .props("dark outlined dense color=teal-4")
                    .style("min-width: 200px;")
                )
                spectype_select = (
                    ui.select(
                        options=["All"] + [tt.value for tt in _SPEC_TESTTYPES],
                        value=initial_spectype,
                        label="Test Type",
                    )
                    .props(SELECT_INPUT_PROPS)
                    .style("min-width: 140px;")
                )

            @ui.refreshable
            def spec_list() -> None:
                raw_stage = str(stage_select.value)
                raw_search = str(testobject_input.value or "").strip().lower()
                raw_type = str(spectype_select.value)

                specs_by_stage = controller.specs(domain)
                flat: list[tuple[str, SpecEntryDTO]] = []
                for s, entries in specs_by_stage.items():
                    if raw_stage != "All" and s != raw_stage:
                        continue
                    for entry in entries:
                        if raw_search and raw_search not in entry.testobject_name.lower():
                            continue
                        if raw_type != "All" and raw_type != entry.testtype.value:
                            continue
                        flat.append((s, entry))

                flat.sort(key=lambda x: (x[1].testobject_name, x[1].testtype.value, x[0]))

                if not flat:
                    ui.label("No specs found.").classes(
                        "text-slate-500 text-xs font-mono mt-4"
                    )
                    return
                for s, entry in flat:
                    _render_spec_card(s, entry)

            spec_list()

            stage_select.on("update:model-value", lambda _: spec_list.refresh())
            testobject_input.on("update:model-value", lambda _: spec_list.refresh())
            spectype_select.on("update:model-value", lambda _: spec_list.refresh())

            async def _bg_refresh() -> None:
                """Periodic background reload — TTL guards prevent over-fetching."""
                await controller.load_backend_data(domain)
                spec_list.refresh()

            bg_timer = ui.timer(5.0, _bg_refresh)
            ui.context.client.on_disconnect(lambda: bg_timer.cancel())
