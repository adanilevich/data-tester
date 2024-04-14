from src.testcase.ports.i_notifier import INotifier


class StdoutNotifier(INotifier):
    def notify(self, message: str, **kwargs):
        print(message)
