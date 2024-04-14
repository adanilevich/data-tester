from src.testcase.adapters.notifiers import InMemoryNotifier


def test_notifying():
    notifier = InMemoryNotifier()
    messages = ["message1", "message2"]
    for message in messages:
        notifier.notify(message)

    assert messages == notifier.notifications
