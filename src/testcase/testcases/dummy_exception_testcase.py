from src.testcase.testcases.testcase import TestCase


class DummyExceptionTestCase(TestCase):
    """This testcase always returns ok -- test purpose only."""
    ttype = "DUMMY_EXCEPTION"
    required_specs = []
    preconditions = []

    def _execute(self):
        self.update_summary("This testcase always raises an Exception.")
        for detail in [{"detail_1_key": "detail 1", "detail_2_key": "detail 2"}]:
            self.add_detail(detail)
        raise ValueError("Testcase 'DUMMY_EXCEPTION' always raises an error.")
