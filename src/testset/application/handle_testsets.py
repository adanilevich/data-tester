from typing import List
from src.testset.core import TestSet
from src.testset.ports import (
    ITestSetCommandHandler,
    SaveTestSetCommand,
    LoadTestSetCommand,
    ListTestSetsCommand,
)
from src.dtos.testset import TestSetDTO
from src.storage.i_storage import IStorage


class TestSetCommandHandler(ITestSetCommandHandler):
    def __init__(self, storage: IStorage):
        self.storage = storage
        self.testset = TestSet(storage)

    def save_testset(self, command: SaveTestSetCommand) -> None:
        self.testset.save_testset(testset=command.testset, location=command.location)

    def load_testset(self, command: LoadTestSetCommand) -> TestSetDTO:
        return self.testset.retrieve_testset(
            testset_id=command.testset_id, location=command.location
        )

    def list_testsets(self, command: ListTestSetsCommand) -> List[TestSetDTO]:
        return self.testset.list_testsets(
            location=command.location, domain=command.domain
        )
