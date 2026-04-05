import threading
from typing import List

from src.dtos import NotificationDTO
from src.infrastructure_ports import INotifier


class InMemoryNotifier(INotifier):
    """In memory notifier, which stores to memory. For test purpose only."""

    def __init__(self):
        self.notifications: List[NotificationDTO] = []
        self._lock = threading.Lock()

    def notify(self, notification: NotificationDTO) -> None:
        with self._lock:
            self.notifications.append(notification)
