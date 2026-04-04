import json
import logging

from src.dtos import NotificationDTO, NotificationProcess, Importance
from src.infrastructure.notifier import LogNotifier


class TestLogNotifier:
    def setup_method(self):
        """Reset the datatester logger between tests."""
        logger = logging.getLogger("datatester")
        logger.handlers.clear()

    def test_notify_logs_at_correct_level(self, caplog):
        notifier = LogNotifier(level="DEBUG")
        notification = NotificationDTO(
            process=NotificationProcess.TESTCASE,
            importance=Importance.WARNING,
            message="test warning",
        )

        with caplog.at_level(logging.DEBUG, logger="datatester"):
            notifier.notify(notification)

        assert len(caplog.records) == 1
        assert caplog.records[0].levelno == logging.WARNING
        assert caplog.records[0].message == "test warning"

    def test_notify_includes_extra_fields(self, caplog):
        notifier = LogNotifier(level="DEBUG")
        notification = NotificationDTO(
            process=NotificationProcess.TESTRUN,
            domain="payments",
            testrun_id="run-123",
            testcase_id="tc-456",
            message="test message",
        )

        with caplog.at_level(logging.DEBUG, logger="datatester"):
            notifier.notify(notification)

        record = caplog.records[0]
        assert record.process_name == "TestRun"  # type: ignore[attr-defined]
        assert record.domain == "payments"  # type: ignore[attr-defined]
        assert record.testrun_id == "run-123"  # type: ignore[attr-defined]
        assert record.testcase_id == "tc-456"  # type: ignore[attr-defined]

    def test_level_filtering(self, capsys):
        notifier = LogNotifier(level="WARNING")
        info_notification = NotificationDTO(
            process=NotificationProcess.SYSTEM,
            importance=Importance.INFO,
            message="should be filtered",
        )
        warning_notification = NotificationDTO(
            process=NotificationProcess.SYSTEM,
            importance=Importance.WARNING,
            message="should appear",
        )

        notifier.notify(info_notification)
        notifier.notify(warning_notification)

        captured = capsys.readouterr()
        assert "should be filtered" not in captured.err
        assert "should appear" in captured.err

    def test_invalid_level_falls_back_to_info(self, capsys):
        notifier = LogNotifier(level="BANANA")
        debug_notification = NotificationDTO(
            process=NotificationProcess.SYSTEM,
            importance=Importance.DEBUG,
            message="should be filtered",
        )
        info_notification = NotificationDTO(
            process=NotificationProcess.SYSTEM,
            importance=Importance.INFO,
            message="should appear",
        )

        notifier.notify(debug_notification)
        notifier.notify(info_notification)

        captured = capsys.readouterr()
        assert "should be filtered" not in captured.err
        assert "should appear" in captured.err

    def test_text_format(self, capsys):
        notifier = LogNotifier(level="DEBUG", structured=False)
        notification = NotificationDTO(
            process=NotificationProcess.TESTCASE,
            importance=Importance.INFO,
            message="hello world",
        )

        notifier.notify(notification)

        captured = capsys.readouterr()
        assert "[INFO]" in captured.err
        assert "[TestCase]" in captured.err
        assert "hello world" in captured.err

    def test_json_format(self, capsys):
        notifier = LogNotifier(level="DEBUG", structured=True)
        notification = NotificationDTO(
            process=NotificationProcess.REPORT,
            domain="finance",
            importance=Importance.ERROR,
            message="report failed",
        )

        notifier.notify(notification)

        captured = capsys.readouterr()
        log_entry = json.loads(captured.err.strip())
        assert log_entry["level"] == "ERROR"
        assert log_entry["process"] == "Report"
        assert log_entry["domain"] == "finance"
        assert log_entry["message"] == "report failed"

    def test_all_importance_levels(self, caplog):
        notifier = LogNotifier(level="DEBUG")

        with caplog.at_level(logging.DEBUG, logger="datatester"):
            for importance in Importance:
                notification = NotificationDTO(
                    process=NotificationProcess.SYSTEM,
                    importance=importance,
                    message=f"{importance.name} msg",
                )
                notifier.notify(notification)

        assert len(caplog.records) == 5
        levels = [r.levelno for r in caplog.records]
        assert levels == [10, 20, 30, 40, 50]
