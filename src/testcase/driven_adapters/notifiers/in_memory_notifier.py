from typing import List

from src.testcase.driven_ports.i_notifier import INotifier


class InMemoryNotifier(INotifier):
    """In memory notifier, which stores to memory. For test purpose only."""

    def __init__(self):
        self.notifications: List[str] = []

    def notify(self, message: str, **kwargs):
        self.notifications.append(message)
