from typing import List, cast
from datetime import datetime

from src.storage.i_storage_factory import IStorageFactory
from src.dtos import TestSetDTO, LocationDTO, StorageObject


class TestSet:
    """
    Handles creation, retrieval, saving, and listing of TestSetDTOs using a Storage.
    """

    def __init__(self, storage_factory: IStorageFactory):
        self.storage_factory = storage_factory

    def save_testset(self, testset: TestSetDTO, location: LocationDTO) -> None:
        """
        Saves a TestSetDTO to the specified location using structured storage.
        """
        testset.last_updated = datetime.now()
        storage = self.storage_factory.get_storage(location)
        storage.write(
            dto=testset,
            object_type=StorageObject.TESTSET,
            location=location
        )

    def retrieve_testset(self, testset_id: str, location: LocationDTO) -> TestSetDTO:
        """
        Retrieves a TestSetDTO by testset_id from the specified location.
        """
        storage = self.storage_factory.get_storage(location)
        dto = storage.read(
            object_type=StorageObject.TESTSET,
            object_id=testset_id,
            location=location
        )
        return cast(TestSetDTO, dto)

    def list_testsets(self, location: LocationDTO, domain: str) -> List[TestSetDTO]:
        """
        Lists all TestSetDTOs in the specified location that match the provided
        domain name.
        """
        storage = self.storage_factory.get_storage(location)
        object_locations = storage.list(
            location=location, object_type=StorageObject.TESTSET
        )
        result = []
        for obj_loc in object_locations:
            try:
                dto = storage.read(
                    object_type=StorageObject.TESTSET,
                    object_id=obj_loc.located_object_id,
                    location=location
                )
                testset = cast(TestSetDTO, dto)
                if testset.domain == domain:
                    result.append(testset)
            except Exception:
                continue  # skip objects that can't be read
        return result
