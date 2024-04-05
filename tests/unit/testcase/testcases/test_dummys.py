from src.testcase.testcases.abstract_testcase import AbstractTestCase


class TestDummyTestcases:

    def test_ok_testcase(self, testcase_creator):
        testcase: AbstractTestCase = testcase_creator(ttype="DUMMY_OK")
        testcase.execute()
        assert testcase.summary == "This testcase always returns OK."
        assert testcase.status == testcase.status.FINISHED
        assert testcase.result == testcase.result.OK

    def test_nok_testcase(self, testcase_creator):
        testcase: AbstractTestCase = testcase_creator(ttype="DUMMY_NOK")
        testcase.execute()
        assert testcase.summary == "This testcase always returns NOK."
        assert testcase.status == testcase.status.FINISHED
        assert testcase.result == testcase.result.NOK

    def test_exception_testcase(self, testcase_creator):
        testcase: AbstractTestCase = testcase_creator(ttype="DUMMY_EXCEPTION")
        testcase.execute()
        assert testcase.summary == "This testcase always raises an Exception."
        assert testcase.status == testcase.status.ERROR
        assert testcase.result == testcase.result.NA
