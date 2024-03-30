from src.testcase.domain.testcase import INotifier


class StdoutNotifier(INotifier):
    def notify(self, message: str):
        print(message)
