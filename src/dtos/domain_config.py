from typing import List, Dict, Optional, Any

from src.dtos.dto import DTO
from src.dtos.location import LocationDTO


class SchemaTestCaseConfigDTO(DTO):
    compare_datatypes: List[str]


class CompareTestCaseConfigDTO(DTO):
    sample_size: int
    sample_size_per_object: Dict[str, int] = dict()


class TestCasesConfigDTO(DTO):
    schema: SchemaTestCaseConfigDTO  # type: ignore
    compare: CompareTestCaseConfigDTO


class DomainConfigDTO(DTO):
    """
    This represents the business-related configuration for test execution for a domain.
    """
    domain: str  # domain name
    instances: Dict[str, List[str]]  # list of domain instance names per stage
    specifications_locations: (  # user-managed locations for specifications, can be ...
        LocationDTO |  # a single location
        List[LocationDTO] |  # a list of locations, e.g. by type or DWH layers
        Dict[str, LocationDTO] |  # a dict of locations by stage
        Dict[str, List[LocationDTO]]  # list or locations by stage.instance
    )
    testreports_location: LocationDTO  # storage location for user-facing reports
    testcases: TestCasesConfigDTO  # testcase specific configuration

    def _item_as_list(self, input: LocationDTO | List[LocationDTO]) -> List[LocationDTO]:
        if isinstance(input, LocationDTO):
            return [input]
        elif isinstance(input, list):
            return input
        else:
            raise ValueError("Input must be string or list of strings.")

    def specifications_locations_by_instance(
            self, stage: str, instance: str) -> List[LocationDTO]:

        if isinstance(self.specifications_locations, (LocationDTO, list)):
            return self._item_as_list(self.specifications_locations)
        else:
            try:
                result = self.specifications_locations[f"{stage}.{instance}"]
                return self._item_as_list(result)
            except KeyError as err:
                msg = "Specifications locations undefined for stage.instance=" \
                    f"{stage}.{instance}"
                raise KeyError(msg) from err
