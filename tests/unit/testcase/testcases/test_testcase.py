from src.testcase.precondition_checks import IPreconditionChecker, ICheckable
from src.dtos import TestCaseResultDTO, TestType


class DummyChecker(IPreconditionChecker):
    def check(self, check: str, checkable: ICheckable) -> bool:
        if check == "must_fail":
            return False
        else:
            return True


# noinspection PyUnresolvedReferences
class TestExecutingTestcases:

    def test_handling_fulfilled_preconditions(self, testcase_creator):
        testcase = testcase_creator.create(ttype=TestType.DUMMY_OK)

        testcase.required_specs = []
        testcase.preconditions = ["ok", "any"]
        check_result = testcase._check_preconditions(checker=DummyChecker())

        assert check_result is True
        assert testcase.status.name == "PRECONDITIONS"
        for check in testcase.preconditions:
            msg = f"Checking that {check.replace('_', ' ')} ..."
            assert msg in testcase.notifiers[0].notifications

    def test_handling_nok_preconditions(self, testcase_creator):
        testcase = testcase_creator.create(ttype=TestType.DUMMY_OK)

        testcase.required_specs = []
        testcase.preconditions = ["any", "must_fail"]
        check_result = testcase._check_preconditions(checker=DummyChecker())

        assert check_result is False
        assert testcase.status.name == "ABORTED"
        msgs = testcase.notifiers[0].notifications
        assert "Any: True" in msgs
        assert "Stopping execution due to failed precondition: must fail!" in msgs

    def test_handling_when_specs_are_provided(self, testcase_creator):
        testcase = testcase_creator.create(ttype=TestType.DUMMY_OK)
        for index, spec in enumerate(testcase.specs):
            if index == 0:
                spec.type = "sql"
            else:
                spec.type = "schema"

        testcase.required_specs = ["sql", "schema"]
        testcase.preconditions = []
        check_result = testcase._check_preconditions(checker=DummyChecker())

        assert check_result is True
        assert testcase.status.name == "PRECONDITIONS"

    def test_execution_with_unfilfilled_preconditions(self, testcase_creator):
        testcase = testcase_creator.create(ttype=TestType.DUMMY_OK)

        testcase.required_specs = []
        testcase.preconditions = ["must_fail"]
        result = testcase.execute(checker=DummyChecker())

        assert testcase.status.name == "ABORTED"
        assert testcase.result.name == "NA"
        assert isinstance(result, TestCaseResultDTO)

    def test_execution_with_exception(self, testcase_creator):
        testcase = testcase_creator.create(ttype=TestType.DUMMY_OK)

        # substitute _execute method with an exception raiser
        # noinspection PyUnusedLocal
        def exc(*args, **kwarts):
            raise ValueError("Dummy Error!")

        testcase._execute = exc

        testcase.required_specs = []
        testcase.preconditions = []
        result = testcase.execute(checker=DummyChecker())

        assert testcase.status.name == "ERROR"
        assert testcase.result.name == "NA"
        assert isinstance(result, TestCaseResultDTO)

    def test_execution_when_everything_is_ok(self, testcase_creator):
        testcase = testcase_creator.create(ttype=TestType.DUMMY_OK)

        testcase.required_specs = []
        testcase.preconditions = []
        result = testcase.execute(checker=DummyChecker())

        assert testcase.status.name == "FINISHED"
        assert testcase.result.name == "OK"
        assert isinstance(result, TestCaseResultDTO)

    def test_adding_details(self, testcase_creator):
        testcase = testcase_creator.create(ttype=TestType.DUMMY_OK)
        detail_1 = {"detail1": "data_1"}
        detail_2 = {"detail2": "data_2"}
        testcase.add_detail(detail_1)
        testcase.add_detail(detail_2)

        assert detail_1 in testcase.details
        assert detail_2 in testcase.details
        assert len(testcase.details) == 2

    def test_updating_summary(self, testcase_creator):
        testcase = testcase_creator.create(ttype=TestType.DUMMY_OK)
        testcase.update_summary("new summary")
        assert testcase.summary == "new summary"
