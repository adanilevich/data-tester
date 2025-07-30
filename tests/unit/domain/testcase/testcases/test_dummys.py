from src.domain.testcase.testcases import AbstractTestCase
from src.dtos import TestType


class TestDummyTestcases:
    def test_ok_testcase(self, testcase_creator):
        testcase: AbstractTestCase = testcase_creator.create(ttype=TestType.DUMMY_OK)
        testcase.execute()
        assert testcase.summary == "This testcase always returns OK."
        assert testcase.status == testcase.status.FINISHED
        assert testcase.result == testcase.result.OK

    def test_nok_testcase(self, testcase_creator):
        testcase: AbstractTestCase = testcase_creator.create(ttype=TestType.DUMMY_NOK)
        testcase.execute()
        assert testcase.summary == "This testcase always returns NOK."
        assert testcase.status == testcase.status.FINISHED
        assert testcase.result == testcase.result.NOK

    def test_exception_testcase(self, testcase_creator):
        testcase: AbstractTestCase = testcase_creator.create(
            ttype=TestType.DUMMY_EXCEPTION
        )
        testcase.execute()
        assert "always raises an error" in testcase.summary
        assert testcase.status == testcase.status.ERROR
        assert testcase.result == testcase.result.NA
