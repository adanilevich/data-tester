"""Shared testobject × testtype matrix table scaffold."""

from collections.abc import Callable

from nicegui import ui

from src.dtos import TestType
from src.ui.styles import TABLE_HEADER_BORDER_STYLE, TABLE_ROW_BORDER_STYLE


def render_testobject_matrix(
    rows: list[str],
    columns: list[TestType],
    cell_fn: Callable[[str, TestType], None],
) -> None:
    """Render a testobject × testtype matrix table.

    rows: sorted testobject names (row headers)
    columns: sorted TestType values (column headers)
    cell_fn: called for each (testobject, testtype) cell — renders cell content
    """
    with ui.element("table").style(
        "width: 100%; border-collapse: collapse; font-family: monospace;"
    ):
        with ui.element("thead"):
            with ui.element("tr"):
                with (
                    ui.element("th")
                    .style(
                        "text-align: left; padding: 4px 8px; "
                        "color: #64748b; font-size: 0.65rem; font-weight: 600;"
                    )
                    .style(TABLE_HEADER_BORDER_STYLE)
                ):
                    ui.label("TESTOBJECT")
                for tt in columns:
                    with (
                        ui.element("th")
                        .style(
                            "text-align: center; padding: 4px 8px; "
                            "color: #64748b; font-size: 0.65rem; "
                            "font-weight: 600; white-space: nowrap;"
                        )
                        .style(TABLE_HEADER_BORDER_STYLE)
                    ):
                        ui.label(tt.value)

        with ui.element("tbody"):
            for obj in rows:
                with ui.element("tr").style(TABLE_ROW_BORDER_STYLE):
                    with ui.element("td").style(
                        "padding: 4px 8px; color: #94a3b8; "
                        "font-size: 0.7rem; white-space: nowrap;"
                    ):
                        ui.label(obj)
                    for tt in columns:
                        with ui.element("td").style(
                            "text-align: center; padding: 4px 8px;"
                        ):
                            cell_fn(obj, tt)
