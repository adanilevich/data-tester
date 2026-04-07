from __future__ import annotations

from uuid import uuid4

import pytest
from src.domain.testrun.testcases import (
    AbstractTestCase,
    CompareTestCase,
    DummyExceptionTestCase,
    DummyNokTestCase,
    DummyOkTestCase,
    RowCountTestCase,
    SchemaTestCase,
    StageCountTestCase,
)
from src.dtos import TestType
from src.dtos.specification_dtos import SpecDTO, SpecType
from src.dtos.storage_dtos import LocationDTO
from src.dtos.testrun_dtos import TestCaseDefDTO
from src.infrastructure.backend.dummy import DummyBackend
from src.infrastructure.notifier import InMemoryNotifier


@pytest.fixture
def testcase_creator(domain_config, testobject):  # noqa: ANN201
    class TestCaseCreator:
        def create(self, ttype: TestType) -> AbstractTestCase:
            testcase_class: type[AbstractTestCase]
            if ttype == TestType.SCHEMA:
                spec_type = SpecType.SCHEMA
                testcase_class = SchemaTestCase
            elif ttype == TestType.ROWCOUNT:
                spec_type = SpecType.ROWCOUNT
                testcase_class = RowCountTestCase
            elif ttype == TestType.COMPARE:
                spec_type = SpecType.COMPARE
                testcase_class = CompareTestCase
            elif ttype == TestType.STAGECOUNT:
                spec_type = SpecType.STAGECOUNT
                testcase_class = StageCountTestCase
            elif ttype == TestType.DUMMY_OK:
                testcase_class = DummyOkTestCase
                spec_type = SpecType.SCHEMA
            elif ttype == TestType.DUMMY_NOK:
                testcase_class = DummyNokTestCase
                spec_type = SpecType.SCHEMA
            elif ttype == TestType.DUMMY_EXCEPTION:
                testcase_class = DummyExceptionTestCase
                spec_type = SpecType.SCHEMA
            else:
                raise ValueError(f"Conftest: Invalid test type: {ttype}")

            definition = TestCaseDefDTO(
                testobject=testobject,
                testtype=ttype,
                specs=[
                    SpecDTO.from_type(
                        spec_type,
                        location=LocationDTO("memory://my_location"),
                        testobject=testobject.name,
                    ),
                    SpecDTO.from_type(
                        spec_type,
                        location=LocationDTO("memory://my_location"),
                        testobject=testobject.name,
                    ),
                ],
                domain_config=domain_config,
                labels=["my_label", "my_label2"],
            )

            return testcase_class(
                definition=definition,
                testrun_id=uuid4(),
                backend=DummyBackend(),
                notifiers=[InMemoryNotifier()],
            )

    return TestCaseCreator()
