from abc import ABC, abstractmethod


class INotifier(ABC):
    """
    Notifies users about actions performed by Testcases. Abstracts underlying infra-
    structure, e.g. WebSockets, EventBuses, etc.
    """

    # TODO: think better about required abstraction level, e.g. if writing to files -
    # do we need to name file by domain, etc.; if writing to logs do we need structured
    # logging; this will impact the signature of the interface
    @abstractmethod
    def notify(self, message: str):
        pass
