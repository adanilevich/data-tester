from src.dtos import Importance, NotificationDTO, NotificationProcess
from src.infrastructure.notifier import InMemoryNotifier


def test_notifying():
    notifier = InMemoryNotifier()
    notifications = [
        NotificationDTO(process=NotificationProcess.TESTCASE, message="message1"),
        NotificationDTO(process=NotificationProcess.TESTRUN, message="message2"),
    ]
    for notification in notifications:
        notifier.notify(notification)

    assert len(notifier.notifications) == 2
    assert notifier.notifications[0].message == "message1"
    assert notifier.notifications[0].process == NotificationProcess.TESTCASE
    assert notifier.notifications[1].message == "message2"
    assert notifier.notifications[1].process == NotificationProcess.TESTRUN
    assert all(n.importance == Importance.INFO for n in notifier.notifications)
