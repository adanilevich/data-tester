import json
import logging
from datetime import datetime

from src.dtos import NotificationDTO
from src.infrastructure_ports import INotifier


class JsonFormatter(logging.Formatter):
    """Formats log records as JSON for structured logging in production."""

    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": record.levelname,
            "process": getattr(record, "process_name", ""),
            "domain": getattr(record, "domain", ""),
            "testrun_id": getattr(record, "testrun_id", ""),
            "testcase_id": getattr(record, "testcase_id", ""),
            "message": record.getMessage(),
        }
        return json.dumps(log_entry)


class LogNotifier(INotifier):
    """Notifier that logs notifications via Python's logging module."""

    def __init__(
        self,
        level: str = "INFO",
        structured: bool = False,
    ):
        self.logger = logging.getLogger("datatester")
        numeric_level = getattr(logging, level.upper(), None)
        if not isinstance(numeric_level, int):
            numeric_level = logging.INFO
        self.logger.setLevel(numeric_level)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            if structured:
                handler.setFormatter(JsonFormatter())
            else:
                handler.setFormatter(logging.Formatter(
                    fmt="[%(asctime)s] [%(levelname)s]"
                    " [%(process_name)s] %(message)s",
                    datefmt="%H:%M:%S",
                    defaults={"process_name": "System"},
                ))
            self.logger.addHandler(handler)

    def notify(self, notification: NotificationDTO) -> None:
        self.logger.log(
            notification.importance.value,
            notification.message,
            extra={
                "process_name": notification.process.value,
                "domain": notification.domain,
                "testrun_id": notification.testrun_id,
                "testcase_id": notification.testcase_id,
            },
        )
