from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class Importance(Enum):
    DEBUG = 10
    INFO = 20
    WARNING = 30
    ERROR = 40
    CRITICAL = 50


class NotificationProcess(Enum):
    TESTCASE = "TestCase"
    TESTRUN = "TestRun"
    TESTSET = "TestSet"
    SPECIFICATION = "Specification"
    REPORT = "Report"
    SYSTEM = "System"


class NotificationDTO(BaseModel):
    timestamp: datetime = Field(default_factory=datetime.now)
    domain: str = Field(default="")
    process: NotificationProcess
    testrun_id: str = Field(default="")
    testcase_id: str = Field(default="")
    importance: Importance = Field(default=Importance.INFO)
    message: str
