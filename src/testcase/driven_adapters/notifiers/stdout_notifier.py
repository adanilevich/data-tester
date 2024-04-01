from src.testcase.driven_ports.notifier_interface import INotifier


class StdoutNotifier(INotifier):
    def notify(self, message: str):
        print(message)
