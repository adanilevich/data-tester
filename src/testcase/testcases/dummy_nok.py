from src.testcase.testcases.abstract_testcase import AbstractTestCase


class DummyNokTestCase(AbstractTestCase):
    """This testcase always returns ok -- test purpose only."""
    ttype = "DUMMY_NOK"
    required_specs = []
    preconditions = []

    def _execute(self):
        self.update_summary("This testcase always returns NOK.")
        for detail in [{"detail_1_key": "detail 1", "detail_2_key": "detail 2"}]:
            self.add_detail(detail)
        self.result = self.result.NOK
        self.status = self.status.FINISHED
