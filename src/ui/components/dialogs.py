"""Shared dialog base component."""

from contextlib import contextmanager
from typing import Generator

from nicegui import ui


@contextmanager
def base_dialog(title: str) -> Generator[ui.dialog, None, None]:
    """Context manager that creates a styled dialog with a title and close button.

    Opens the dialog on exit. Usage::

        with base_dialog("My Title") as dlg:
            ui.label("Content")
    """
    with ui.dialog() as dlg:
        with ui.card().style(
            "min-width: 600px; max-width: 90vw; "
            "background: #161b27; border: 1px solid #334155;"
        ):
            with (
                ui.row()
                .classes("items-center justify-between w-full")
                .style("margin-bottom: 0.75rem;")
            ):
                ui.label(title).classes(
                    "text-white font-mono font-bold text-base tracking-widest"
                )
                ui.button(icon="close", on_click=dlg.close).props(
                    "flat round dense"
                ).classes("text-slate-400")
            yield dlg
    dlg.open()
