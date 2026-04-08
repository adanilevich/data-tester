from typing import Callable

from nicegui import ui
from pydantic import BaseModel


class Reusable(BaseModel):
    id: str

    label: str
    on_click_callback: Callable[["Reusable"], None]

    _input_value: str = ""

    def render(self) -> ui.card:
        with ui.card() as card:
            ui.input(label=self.label).bind_value(self, "_input_value").on(
                "keydown.enter", self.on_click
            )
            ui.button("GO", on_click=self.on_click)
        return card

    def on_click(self):
        ui.notify(f"{self.id} clicked with {self._input_value}!")
        self.on_click_callback(self)


@ui.page("/")
def main():
    label_text = {"text": "The Label"}
    ui.label("The Label").bind_text(label_text)

    with ui.card():
        Reusable(
            id="a",
            label="Print something",
            on_click_callback=lambda x: print(x._input_value),
        ).render()
        Reusable(
            id="b",
            label="Change The Label",
            on_click_callback=lambda x: label_text.update({"text": x._input_value}),
        ).render()


ui.run()
