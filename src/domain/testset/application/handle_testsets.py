from typing import List
from src.domain.testset.core import TestSet
from src.domain.testset.ports import (
    ITestSetCommandHandler,
    SaveTestSetCommand,
    LoadTestSetCommand,
    ListTestSetsCommand,
)
from src.dtos import TestSetDTO
from src.infrastructure.storage import IStorageFactory


class TestSetCommandHandler(ITestSetCommandHandler):
    def __init__(self, storage_factory: IStorageFactory):
        self.storage_factory = storage_factory
        self.testset = TestSet(storage_factory)

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
