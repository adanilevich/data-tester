from src.infrastructure_ports import INotifier


class StdoutNotifier(INotifier):
    def notify(self, message: str, **kwargs):
        print(message)
