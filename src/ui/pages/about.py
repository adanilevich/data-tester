"""About page — route: /about"""

import re
from pathlib import Path

from nicegui import ui

from src.ui.client import DataTesterClient
from src.ui.components import NavBar, StatusBar
from src.ui.controller import Controller, NiceGuiState

_README: Path = Path(__file__).parents[3] / "README.md"


def _prepare_readme(text: str) -> str:
    """Strip badge lines and the ## Run section from README text."""
    # Remove badge image lines (e.g. ![tests](badges/tests.svg))
    text = re.sub(r"^!\[.*?\]\(badges/.*?\)\s*\n?", "", text, flags=re.MULTILINE)
    # Remove the ## Run section up to (but not including) the next ## heading or EOF
    text = re.sub(r"## Run\b.*?(?=^## |\Z)", "", text, flags=re.DOTALL | re.MULTILINE)
    return text.strip()


def register(client: DataTesterClient) -> None:
    """Register the about page route."""

    @ui.page("/about")
    async def about_page() -> None:
        controller = Controller(client=client, state=NiceGuiState())
        NavBar(controller).render()
        StatusBar(controller).render()

        content = _README.read_text(encoding="utf-8") if _README.exists() else (
            "_README.md not found._"
        )

        with ui.column().classes(
            "w-full min-h-screen bg-[#0f1117] px-6 py-8 items-center"
        ):
            with ui.card().classes(
                "w-full max-w-4xl bg-[#161b27] border border-slate-700 "
                "rounded-xl shadow-2xl p-8"
            ).props("flat"):
                ui.markdown(_prepare_readme(content)).classes(
                    "prose prose-invert max-w-none"
                )
