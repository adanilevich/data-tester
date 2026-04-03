from typing import List
from src.domain.testset.testset import TestSet
from src.domain_ports import (
    ITestSet,
    SaveTestSetCommand,
    LoadTestSetCommand,
    ListTestSetsCommand,
)
from src.dtos import TestSetDTO
from src.infrastructure_ports import IDtoStorage


class TestSetAdapter(ITestSet):
    def __init__(self, dto_storage: IDtoStorage):
        self.testset = TestSet(dto_storage)

    def save_testset(self, command: SaveTestSetCommand) -> None:
        self.testset.save_testset(testset=command.testset)

    def load_testset(self, command: LoadTestSetCommand) -> TestSetDTO:
        return self.testset.load_testset(
            testset_id=command.testset_id
        )

    def list_testsets(self, command: ListTestSetsCommand) -> List[TestSetDTO]:
        return self.testset.list_testsets(domain=command.domain)
