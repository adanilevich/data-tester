from typing import List

from src.testcase.ports import IRunTestCasesCommandHandler, RunTestCaseCommand


class CliTestCaseRunner:
    """Runs testcases in batch mode from CLI"""

    def __init__(self, handler: IRunTestCasesCommandHandler):
        self.handler = handler

    def run_testcases(self, testcases: List[dict]) -> List[dict]:

        run_testcase_commands = []
        for testcase in testcases:
            command = RunTestCaseCommand.from_dict(testcase)
            run_testcase_commands.append(command)

        results_as_dtos = self.handler.run(commands=run_testcase_commands)
        results_as_dicts = [result.dict() for result in results_as_dtos]

        return results_as_dicts
