from typing import List, Dict, Optional, Any, Self

from src.dtos import DTO
from src.dtos.location import LocationDTO


class SchemaTestCaseConfigDTO(DTO):
    compare_datatypes: List[str]


class CompareSampleTestCaseConfigDTO(DTO):
    sample_size: int
    sample_size_per_object: Dict[str, int] = dict()


class TestCasesConfigDTO(DTO):
    schema: SchemaTestCaseConfigDTO  # type: ignore
    compare_sample: CompareSampleTestCaseConfigDTO

    @classmethod
    def from_dict(cls, dict_: dict) -> Self:
        schema = dict_["schema"]
        compare_sample = dict_["compare_sample"]

        return cls(
            schema=SchemaTestCaseConfigDTO.from_dict(schema),
            compare_sample=CompareSampleTestCaseConfigDTO.from_dict(compare_sample),
        )

class DomainConfigDTO(DTO):
    """
    This serves as a generic fixtures container for business-related configurations.
    The required attributes are defined by configuration needs of implemented Testcases,
    e.g., the testcase compare_sample requires a sample size definition.
    """
    domain: str
    instances: Dict[str, List[str]]  # dict {stage: [instance1, instance2], ...}
    """
    Specifications can be stored
        - in one location
        - in several locations, e.g. separated by type (sql, excel) or by DWH layers
        - in one location per stage, e.g. different versions for TEST and UAT
        - in several locations per stage
    """
    specifications_locations: (
        LocationDTO |
        List[LocationDTO] |
        Dict[str, LocationDTO] |
        Dict[str, List[LocationDTO]]
    )
    # TODO: change this to a single location which can contain multiple testmatrices
    testmatrices_locations: List[LocationDTO]
    testreports_location: LocationDTO
    testcases: TestCasesConfigDTO
    platform_specific: Optional[Dict[str, Any]] = None

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
