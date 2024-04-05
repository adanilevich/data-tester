from src.testcase.testcases.abstract_testcase import AbstractTestCase


class DummyOkAbstractTestCase(AbstractTestCase):
    """This testcase always returns ok -- test purpose only."""
    ttype = "DUMMY_OK"
    required_specs = []
    preconditions = []

    def _execute(self):

        self.update_summary("This testcase always returns OK.")
        for detail in [{"detail_1_key": "detail 1", "detail_2_key": "detail 2"}]:
            self.add_detail(detail)
        self.result = self.result.OK
        self.status = self.status.FINISHED
