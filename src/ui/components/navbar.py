"""Shared navigation bar component."""

from nicegui import ui
from src.ui.controller import Controller


_NAV_ITEMS = [
    ("Testsets", "/{domain}/testsets"),
    ("Executions", "/{domain}/executions"),
    ("Reports", "/{domain}/reports"),
    ("Specs", "/{domain}/specs"),
    ("Config", "/{domain}/config"),
]

_ACTIVE_LINK = (
    "text-teal-400 border-b-2 border-teal-400 "
    "font-semibold tracking-wide uppercase text-xs px-4 py-3 "
    "transition-colors duration-150"
)
_DISABLED_LINK = (
    "text-slate-600 cursor-not-allowed "
    "font-semibold tracking-wide uppercase text-xs px-4 py-3 "
    "select-none"
)

_SETTINGS_ITEMS = ["First", "Second", "Third"]


class NavBar:

    def __init__(self, controller: Controller):
        self.controller = controller

    def render(self) -> ui.header:
        with ui.header(elevated=True).classes(
            "flex items-center justify-between px-6 py-0 "
            "bg-[#0f1117] border-b border-slate-800 h-14"
        ) as header:
            ui.label("DATA TESTER").classes(
                "text-teal-400 font-mono font-bold tracking-widest text-sm mr-8"
            )

            with ui.row().classes("items-stretch h-14"):
                for label, path_template in _NAV_ITEMS:
                    if self.controller.domain:
                        href = path_template.format(domain=self.controller.domain)
                        ui.link(label, href).classes(_ACTIVE_LINK)
                    else:
                        ui.label(label).classes(_DISABLED_LINK)

            with ui.row().classes("items-center"):
                with ui.button(icon="settings").props("flat dense").classes(
                    "text-slate-400 hover:text-teal-400 transition-colors duration-150"
                ):
                    with ui.menu():
                        for item in _SETTINGS_ITEMS:
                            ui.menu_item(item)
        return header
