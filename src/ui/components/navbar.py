"""Shared navigation bar component."""

from nicegui import ui

from src.ui.controller import Controller
from src.ui.styles import ICON_BUTTON_SECONDARY_CLASSES

_NAV_ITEMS = [
    ("Testsets", "/{domain}/testsets"),
    ("Testruns", "/{domain}/testruns"),
    ("Specs", "/{domain}/specs"),
    ("Config", "/{domain}/config"),
]

_LINK_BASE = (
    "font-semibold tracking-wide uppercase text-xs px-4 py-3 "
    "transition-colors duration-150 border-b-2"
)
_SELECTED_LINK = f"text-white border-teal-400 {_LINK_BASE}"
_NAV_LINK = f"text-slate-400 hover:text-teal-400 border-transparent {_LINK_BASE}"
_DISABLED_LINK = (
    "text-slate-600 cursor-not-allowed "
    "font-semibold tracking-wide uppercase text-xs px-4 py-3 "
    "select-none"
)


class NavBar:
    def __init__(self, controller: Controller):
        self.controller = controller

    def render(self) -> ui.header:
        current_route = ui.context.client.page.path

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
                        is_current = path_template == current_route
                        ui.link(label, href).classes(
                            _SELECTED_LINK if is_current else _NAV_LINK
                        )
                    else:
                        ui.label(label).classes(_DISABLED_LINK)

            with ui.row().classes("items-center"):
                with (
                    ui.button(icon="settings")
                    .props("flat dense")
                    .classes(ICON_BUTTON_SECONDARY_CLASSES)
                ):
                    with ui.menu():
                        ui.menu_item(
                            "Domain Selection",
                            on_click=self._go_to_domain_selection,
                        )
                        ui.menu_item(
                            "About",
                            on_click=lambda: ui.navigate.to("/about"),
                        )
        return header

    def _go_to_domain_selection(self) -> None:
        self.controller.domain = None
        ui.navigate.to("/")
