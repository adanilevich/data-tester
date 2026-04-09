"""Domain selection page — route: /

Fetches all domain configs from the backend via controller, presents a dropdown,
stores the selection in state, and redirects to the domain home page.
"""

from nicegui import ui

from src.ui.client import DataTesterClient
from src.ui.components import NavBar, StatusBar
from src.ui.controller import Controller, NiceGuiState


def register(client: DataTesterClient) -> None:
    """Register the domain-selection page route."""

    @ui.page("/")
    async def domain_selection() -> None:
        controller = Controller(client=client, state=NiceGuiState())
        NavBar(controller).render()
        StatusBar(controller).render()

        error_msg = await controller.load_domains()

        with ui.column().classes(
            "flex-1 flex items-center justify-center min-h-screen "
            "bg-[#0f1117] w-full"
        ):
            with ui.card().classes(
                "bg-[#161b27] border border-slate-700 rounded-xl "
                "shadow-2xl w-full max-w-md p-8"
            ):
                ui.label("Select Domain").classes(
                    "text-white font-mono font-bold text-2xl tracking-widest mb-1"
                )
                ui.label("Choose a domain to begin testing.").classes(
                    "text-slate-500 text-sm mb-8"
                )

                if error_msg:
                    with ui.row().classes("items-center mb-4"):
                        ui.icon("error_outline").classes("text-red-500 mr-2")
                        ui.label(error_msg).classes("text-red-400 text-sm font-mono")

                if not controller.domains:
                    ui.label("No domains available.").classes(
                        "text-slate-500 text-sm font-mono"
                    )
                    return

                select = (
                    ui.select(options=controller.domains, label="Domain")
                    .classes("w-full font-mono")
                    .props("dark outlined dense color=teal-4")
                )

                async def on_confirm() -> None:
                    chosen: str | None = select.value
                    if not chosen:
                        ui.notify("Please select a domain.", type="warning")
                        return
                    controller.domain = chosen
                    ui.navigate.to(f"/{chosen}/testsets")

                ui.button("Confirm", on_click=on_confirm).classes(
                    "mt-6 w-full bg-teal-500 hover:bg-teal-400 "
                    "text-[#0f1117] font-bold font-mono tracking-widest "
                    "rounded-lg py-2 transition-colors duration-150"
                ).props("no-caps")
