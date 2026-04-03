from typing import List, cast
from datetime import datetime

from src.infrastructure_ports import IDtoStorage
from src.dtos import TestSetDTO, ObjectType


class TestSet:
    """
    Handles creation, retrieval, saving, and listing of TestSetDTOs.
    """

    def __init__(self, storage: IDtoStorage):
        self.storage = storage

    def save_testset(self, testset: TestSetDTO) -> None:
        """Saves a TestSetDTO to internal storage."""
        testset.last_updated = datetime.now()
        self.storage.write_dto(dto=testset)

    def load_testset(self, testset_id: str) -> TestSetDTO:
        """Retrieves a TestSetDTO by testset_id."""
        dto = self.storage.read_dto(
            object_type=ObjectType.TESTSET, id=testset_id
        )
        return cast(TestSetDTO, dto)

    def list_testsets(self, domain: str) -> List[TestSetDTO]:
        """
        Lists all TestSetDTOs that match the provided domain name.
        """
        dtos = self.storage.list_dtos(
            object_type=ObjectType.TESTSET,
            filters={"domain": domain},
        )
        return [cast(TestSetDTO, dto) for dto in dtos]
