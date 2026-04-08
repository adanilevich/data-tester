"""Shared status bar component shown at the bottom of every page."""

from nicegui import ui
from src.ui.controller import Controller


class StatusBar:

    def __init__(self, controller: Controller):
        self.controller = controller

    def render(self) -> ui.footer:
        domain = self.controller.domain
        domain_text = f"Domain: {domain}" if domain else "No domain selected"
        dot_color = "bg-teal-400" if domain else "bg-slate-600"

        with ui.footer().classes(
            "flex items-center px-6 py-2 "
            "bg-[#0b0d13] border-t border-slate-800 h-10"
        ) as footer:
            with ui.row().classes("items-center"):
                ui.element("div").classes(
                    f"w-2 h-2 rounded-full {dot_color} mr-2"
                )
                ui.label(domain_text).classes(
                    "font-mono text-xs text-slate-400 tracking-widest"
                )
        return footer


# def build_statusbar(state: State) -> None:
#     """Render the sticky footer status bar into the current page context."""
#     domain: str | None = state.domain

#     domain_text = f"Domain: {domain}" if domain else "No domain selected"
#     dot_color = "bg-teal-400" if domain else "bg-slate-600"

#     with ui.footer().classes(
#         "flex items-center px-6 py-2 "
#         "bg-[#0b0d13] border-t border-slate-800 h-10"
#     ):
#         with ui.row().classes("items-center"):
#             ui.element("div").classes(
#                 f"w-2 h-2 rounded-full {dot_color} mr-2"
#             )
#             ui.label(domain_text).classes(
#                 "font-mono text-xs text-slate-400 tracking-widest"
#             )
