from typing import List
from datetime import datetime

from src.storage.i_storage import IStorage
from src.dtos.testset import TestSetDTO
from src.dtos.location import LocationDTO


class TestSet:
    """
    Handles creation, retrieval, saving, and listing of TestSetDTOs using a Storage.
    """

    def __init__(self, storage: IStorage):
        self.storage = storage

    def _file_location(self, testset_id: str, location: LocationDTO) -> LocationDTO:
        """
        Constructs the file location for a testset given its id and base location.
        """
        filename = f"{testset_id}.json"
        return location.append(filename)

    def save_testset(self, testset: TestSetDTO, location: LocationDTO) -> None:
        """
        Saves a TestSetDTO to the specified location as a json file.
        """
        file_location = self._file_location(str(testset.testset_id), location)
        testset.last_updated = datetime.now()
        testset_bytes = testset.to_json().encode()
        self.storage.write(content=testset_bytes, path=file_location)

    def retrieve_testset(self, testset_id: str, location: LocationDTO) -> TestSetDTO:
        """
        Retrieves a TestSetDTO by testset_id from the specified location.
        """
        file_location = self._file_location(testset_id, location)
        testset_bytes = self.storage.read(file_location)
        return TestSetDTO.from_json(testset_bytes)

    def list_testsets(self, location: LocationDTO, domain: str) -> List[TestSetDTO]:
        """
        Lists all TestSetDTOs in the specified location that match the provided
        domain name.
        """
        testset_locations = self.storage.list(location)
        result = []
        for loc in testset_locations:
            try:
                testset_bytes = self.storage.read(loc)
                testset = TestSetDTO.from_json(testset_bytes)
                if testset.domain == domain:
                    result.append(testset)
            except Exception:
                continue  # skip files that are not valid testsets
        return result
