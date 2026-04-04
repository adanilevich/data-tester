from abc import ABC, abstractmethod

from src.dtos import NotificationDTO


class INotifier(ABC):
    """
    Notifies users about actions performed by domain objects. Abstracts underlying
    infrastructure, e.g. WebSockets, EventBuses, etc.
    """

    @abstractmethod
    def notify(self, notification: NotificationDTO) -> None:
        """
        Notify (users and clients) via sending a structured notification. This can
        mean writing to logs, websockets, files, etc.
        """
